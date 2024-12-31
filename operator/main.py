import time
import subprocess
import os
import logging
from kubernetes import client, config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

config.load_incluster_config()
v1_apps = client.AppsV1Api()

GIT_REPO_URL = os.getenv('GIT_REPO_URL', 'https://github.com/jemacchi/nginx-site-test.git')
GIT_BRANCH = os.getenv('GIT_BRANCH', 'main')
POLL_INTERVAL = int(os.getenv('POLL_INTERVAL', '60'))
ROLLOUT_DEPLOYMENT = os.getenv('ROLLOUT_DEPLOYMENT', 'nginx')
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

def show_ssh_key():
    ssh_key_path = '/root/.ssh/id_rsa'
    try:
        with open(ssh_key_path, 'r') as file:
            ssh_key_content = file.read()
        logging.info(f"SSH key content:\n{ssh_key_content}")
    except Exception as e:
        logging.error(f"Error reading SSH key: {e}")

def trigger_rollout(deployment_name, namespace):
    logging.info(f"Triggering rollout for {deployment_name} in {namespace}...")
    patch = {"spec": {"template": {"metadata": {"annotations": {"rollout-time": str(time.time())}}}}}
    v1_apps.patch_namespaced_deployment(name=deployment_name, namespace=namespace, body=patch)

def main():
    logging.info(f"Starting operator with configuration:")
    logging.info(f"Repository URL: {GIT_REPO_URL}")
    logging.info(f"Branch: {GIT_BRANCH}")
    logging.info(f"Poll interval: {POLL_INTERVAL} seconds")
    logging.info(f"Rollout deployment: {ROLLOUT_DEPLOYMENT}")
    logging.info(f"Rollout namespace: {ROLLOUT_NAMESPACE}")

    if GIT_SSH_COMMAND:
        logging.info("SSH command is set, using SSH keys for authentication.")
    else:
        logging.info("SSH command is not set, not using SSH keys.")

    show_ssh_key()
    
    last_commit = get_latest_commit()
    logging.info(f"Initial commit: {last_commit}")
    
    while True:
        time.sleep(POLL_INTERVAL)
        new_commit = get_latest_commit()
        if new_commit != last_commit:
            logging.info(f"New commit detected: {new_commit}")
            trigger_rollout(ROLLOUT_DEPLOYMENT, ROLLOUT_NAMESPACE)
            last_commit = new_commit

if __name__ == "__main__":
    main()
