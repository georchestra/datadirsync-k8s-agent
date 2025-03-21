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
  - ROLLOUT_NAMESPACE: Kubernetes namespace where the deployments reside.
- Uses Kubernetes API to apply rolling updates when changes are detected.

"""

import time
import subprocess
import os
import logging
import git
import yaml
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
ROLLOUT_NAMESPACE = os.getenv('ROLLOUT_NAMESPACE', 'default')
ROLLOUT_MAPPING_FILE = os.getenv('ROLLOUT_MAPPING_FILE', '/tmp/datadirsync/rollout_mapping_config.yaml')
GIT_USERNAME = os.getenv('GIT_USERNAME', '')
GIT_TOKEN = os.getenv('GIT_TOKEN', '')
GIT_SSH_COMMAND = os.getenv('GIT_SSH_COMMAND', '')


def checkout_repo(repo, branch):
    default_branch = repo.git.rev_parse('--abbrev-ref', 'HEAD')
    remote_branches = [ref.name for ref in repo.remote().refs]
    remote_branch = f'origin/{branch}'

    if branch == default_branch:
        logging.info(f"Branch {branch} is the default branch, already checked out.")
    elif remote_branch in remote_branches:
        logging.info(f"Branch {branch} existing in refs.")
        repo.git.checkout('-b', branch, remote_branch)
        logging.info(f"Checkout of branch {branch} done.")
    else:
        logging.warning(f"Branch {branch} not found in remote. Using default branch.")


def clone_repo(repo_url, branch, clone_path):
    if not os.path.exists(clone_path):
        logging.info("Cloning repository ...")
        os.makedirs(clone_path, exist_ok=True)
        repo = git.Repo.clone_from(repo_url, clone_path)
        logging.info("Repository cloned.")
        checkout_repo(repo, branch)
        logging.info(f"Repository cloned and switched to branch {branch}")

def load_deployment_map(file_path):
    """Load the mapping of folders and files to deployments from a YAML file."""
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def determine_repo_url(git_url, git_username, git_token, git_ssh_command):
    """Determine the git URL based on the authentication method."""
    if git_ssh_command:
        logging.info("Using SSH for git access")
    elif git_username and git_token:
        protocol_separator = "://"
        protocol, repo_path = git_url.split(protocol_separator)
        git_url = f"{protocol}://{git_username}:{git_token}@{repo_path}"
        logging.info("Using authenticated git access")
    else:
        logging.info("Using anonymous git access")
    return git_url

def get_latest_commit(git_url, git_branch, git_ssh_command=None):
    """Retrieve the latest commit hash from the specified Git branch."""

    result = subprocess.run(
        ["git", "ls-remote", git_url, f"refs/heads/{git_branch}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ, 'GIT_SSH_COMMAND': git_ssh_command} if git_ssh_command else None
    )

    if result.returncode != 0:
        logging.error(f"Git command failed: {result.stderr}")
        raise Exception("Failed to get latest commit")

    return result.stdout.split()[0]

def get_changed_files(repo_path, branch, commit_hash, git_ssh_command=None):
    repo = git.Repo(repo_path)
    repo.git.fetch()
    repo.git.checkout(commit_hash)
    """Obtain the list of files changed in the specified commit."""
    result = subprocess.run(
        ["git", "show", "--name-only", commit_hash],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=repo_path,
        env={**os.environ, 'GIT_SSH_COMMAND': git_ssh_command} if git_ssh_command else None
    )

    if result.returncode != 0:
        logging.error(f"Git command failed: {result.stderr}")
        raise Exception("Failed to get changed files")

    files_changed = result.stdout.splitlines()[6:]

    return files_changed

def determine_affected_deployments(changed_files, artifact_to_deployment_map):
    """Determine which deployments should be rolled based on changed files."""
    affected_deployments = set()

    if '*' in artifact_to_deployment_map:
        # If '*' is a key in the map, all changes trigger these deployments
        logging.info("Wildcard '*' detected in deployment map; all changes will trigger associated deployments.")
        affected_deployments.update(artifact_to_deployment_map['*'])

    for changed_file in changed_files:
        # Check if the file itself is mapped
        if changed_file in artifact_to_deployment_map:
            affected_deployments.update(artifact_to_deployment_map[changed_file])

        # Check if the folder is mapped
        folder = changed_file.split('/')[0]
        if folder in artifact_to_deployment_map:
            affected_deployments.update(artifact_to_deployment_map[folder])

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

    repo_url = determine_repo_url(GIT_REPO_URL, GIT_USERNAME, GIT_TOKEN, GIT_SSH_COMMAND)
    repo_local_path = "/tmp/datadir"

    clone_repo(repo_url, GIT_BRANCH, repo_local_path)

    try:
        deployment_map = load_deployment_map(ROLLOUT_MAPPING_FILE)
        latest_commit = get_latest_commit(repo_url, GIT_BRANCH, GIT_SSH_COMMAND)
        logging.info(f"Initial commit: {latest_commit}")

        while True:
            time.sleep(POLL_INTERVAL)
            new_commit = get_latest_commit(repo_url, GIT_BRANCH, GIT_SSH_COMMAND)
            if new_commit != latest_commit:
                logging.info(f"New commit detected: {new_commit}")
                changed_files = get_changed_files(repo_local_path, GIT_BRANCH, new_commit, GIT_SSH_COMMAND)
                affected_deployments = determine_affected_deployments(changed_files, deployment_map)
                if affected_deployments:
                    logging.info(f"Deployments to rollout: {affected_deployments}")
                    trigger_rollout(','.join(affected_deployments), ROLLOUT_NAMESPACE)
                latest_commit = new_commit
    except Exception as e:
        logging.error(str(e))

if __name__ == "__main__":
    main()