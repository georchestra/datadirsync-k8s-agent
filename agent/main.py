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

def get_latest_commit():
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

def show_ssh_key(git_ssh_command):
    match = re.search(r'-i\s+([^\s]+)', git_ssh_command)
    if match:
        ssh_key_path = match.group(1)
        try:
            with open(ssh_key_path, 'r') as file:
                ssh_key_content = file.read()
            logging.info(f"SSH key content:\n{ssh_key_content}")
        except Exception as e:
            logging.error(f"Error reading SSH key: {e}")
    else:
        logging.error("SSH key path not found in GIT_SSH_COMMAND")

def trigger_rollout(deployment_names, namespace):
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
    logging.info(f"Rollout these deployments: {ROLLOUT_DEPLOYMENTS}")
    logging.info(f"Rollout namespace: {ROLLOUT_NAMESPACE}")

    if GIT_SSH_COMMAND:
        logging.info("SSH command is set, using SSH keys for authentication.")
        logging.info(f"Git SSH Command: {GIT_SSH_COMMAND}")
        #show_ssh_key(GIT_SSH_COMMAND)
    else:
        logging.info("SSH command is not set, not using SSH keys.")
    
    last_commit = get_latest_commit()
    logging.info(f"Initial commit: {last_commit}")
    
    while True:
        time.sleep(POLL_INTERVAL)
        new_commit = get_latest_commit()
        if new_commit != last_commit:
            logging.info(f"New commit detected: {new_commit}")
            trigger_rollout(ROLLOUT_DEPLOYMENTS, ROLLOUT_NAMESPACE)
            last_commit = new_commit

if __name__ == "__main__":
    main()
