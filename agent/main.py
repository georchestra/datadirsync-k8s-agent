"""
Git-based Kubernetes Deployment Auto-Rollout Agent

This script monitors a specified Git repository for new commits in a given branch.
When a new commit is detected, it triggers a rollout of one or more Kubernetes
deployments by patching their annotations, forcing a restart of the pods.

Features:
- Supports both SSH and authenticated HTTPS Git access.
- Configurable via environment variables:
  - GIT_REPO_URL: URL of the Git repository to monitor.
  - GIT_BRANCH: Branch to track for changes (default: main).
  - POLL_INTERVAL: Time interval (in seconds) between checks (default: 60).
  - ROLLOUT_DEPLOYMENTS: Comma-separated list of Kubernetes deployments to restart.
  - ROLLOUT_NAMESPACE: Kubernetes namespace where the deployments reside.
- Uses Kubernetes API to apply rolling updates when changes are detected.

"""

import time
import subprocess
import os
import logging
import re
import json
from kubernetes import client, config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

config.load_incluster_config()
v1_apps = client.AppsV1Api()

GIT_REPO_URL = os.getenv('GIT_REPO_URL', '')
GIT_BRANCH = os.getenv('GIT_BRANCH', 'main')
POLL_INTERVAL = int(os.getenv('POLL_INTERVAL', '60'))
ROLLOUT_DEPLOYMENTS = os.getenv('ROLLOUT_DEPLOYMENTS', 'geoserver')
ROLLOUT_NAMESPACE = os.getenv('ROLLOUT_NAMESPACE', 'default')
GIT_USERNAME = os.getenv('GIT_USERNAME', '')
GIT_TOKEN = os.getenv('GIT_TOKEN', '')
GIT_SSH_COMMAND = os.getenv('GIT_SSH_COMMAND', '')

def load_folder_to_deployment_map(file_path):
    """Load the mapping of folders and files to deployments from a JSON file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def get_latest_commit():
    """Retrieve the latest commit hash from the specified Git branch."""
    git_url = GIT_REPO_URL

    if GIT_SSH_COMMAND:
        logging.info("Using SSH for git access")
    elif GIT_USERNAME and GIT_TOKEN:
        protocol_separator = "://"
        protocol, repo_path = git_url.split(protocol_separator)
        git_url = f"{protocol}://{GIT_USERNAME}:{GIT_TOKEN}@{repo_path}"
        logging.info("Using authenticated git access")
    else:
        logging.info("Using anonymous git access")

    result = subprocess.run(
        ["git", "ls-remote", git_url, f"refs/heads/{GIT_BRANCH}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ, 'GIT_SSH_COMMAND': GIT_SSH_COMMAND} if GIT_SSH_COMMAND else None
    )

    if result.returncode != 0:
        logging.error(f"Git command failed: {result.stderr}")
        raise Exception("Failed to get latest commit")
        
    return result.stdout.split()[0]

def get_changed_files(commit_hash):
    """Obtain the list of files changed in the specified commit."""
    result = subprocess.run(
        ["git", "show", "--name-only", commit_hash],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        logging.error(f"Git command failed: {result.stderr}")
        raise Exception("Failed to get changed files")

    files_changed = result.stdout.splitlines()[6:]  # Skip the commit message

    return files_changed

def determine_affected_deployments(changed_files, folder_to_deployment_map):
    """Determine which deployments should be rolled based on changed files."""
    affected_deployments = set()

    for changed_file in changed_files:
        # Check if the file itself is mapped
        if changed_file in folder_to_deployment_map:
            affected_deployments.update(folder_to_deployment_map[changed_file])
        
        # Check if the folder is mapped
        folder = changed_file.split('/')[0]  # Get the folder name
        if folder in folder_to_deployment_map:
            affected_deployments.update(folder_to_deployment_map[folder])

    return list(affected_deployments)

def trigger_rollout(deployment_names, namespace):
    """Trigger a Kubernetes rollout for the specified deployments."""
    deployment_name_list = deployment_names.split(',')

    for deployment_name in deployment_name_list:
        deployment_name = deployment_name.strip()
        logging.info(f"Triggering rollout for {deployment_name} in {namespace}...")
        patch = {"spec": {"template": {"metadata": {"annotations": {"rollout-time": str(time.time())}}}}}
        v1_apps.patch_namespaced_deployment(name=deployment_name, namespace=namespace, body=patch)

def main():
    logging.info(f"Starting agent with configuration:")
    logging.info(f"Repository URL: {GIT_REPO_URL}")
    logging.info(f"Branch: {GIT_BRANCH}")
    logging.info(f"Poll interval: {POLL_INTERVAL} seconds")
    logging.info(f"Rollout namespace: {ROLLOUT_NAMESPACE}")

    if GIT_SSH_COMMAND:
        logging.info("SSH command is set, using SSH keys for authentication.")
        logging.info(f"Git SSH Command: {GIT_SSH_COMMAND}")
        #show_ssh_key(GIT_SSH_COMMAND)
    else:
        logging.info("SSH command is not set, not using SSH keys.")
        
    try:
        folder_to_deployment_map = load_folder_to_deployment_map('folder_to_deployment_map.json')
        latest_commit = get_latest_commit()
        logging.info(f"Initial commit: {latest_commit}")
        
        while True:
            time.sleep(POLL_INTERVAL)
            new_commit = get_latest_commit()
            if new_commit != latest_commit:
                logging.info(f"New commit detected: {new_commit}")
                changed_files = get_changed_files(new_commit)
                affected_deployments = determine_affected_deployments(changed_files, folder_to_deployment_map)
                if affected_deployments:
                    logging.info(f"Deployments to rollout: {affected_deployments}")
                    trigger_rollout(','.join(affected_deployments), ROLLOUT_NAMESPACE)
                latest_commit = new_commit
    except Exception as e:
        logging.error(str(e))

if __name__ == "__main__":
    main()