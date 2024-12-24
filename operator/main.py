import time
import subprocess
from kubernetes import client, config

config.load_incluster_config()
v1_apps = client.AppsV1Api()

GIT_REPO_URL = "https://github.com/jemacchi/nginx-site-test.git"
GIT_BRANCH = "main"
POLL_INTERVAL = 60

def get_latest_commit():
    result = subprocess.run(
        ["git", "ls-remote", GIT_REPO_URL, f"refs/heads/{GIT_BRANCH}"],
        stdout=subprocess.PIPE,
        text=True,
    )
    return result.stdout.split()[0]

def trigger_rollout(deployment_name, namespace):
    print(f"Triggering rollout for {deployment_name} in {namespace}...")
    patch = {"spec": {"template": {"metadata": {"annotations": {"rollout-time": str(time.time())}}}}}
    v1_apps.patch_namespaced_deployment(name=deployment_name, namespace=namespace, body=patch)

def main():
    last_commit = get_latest_commit()
    print(f"Initial commit: {last_commit}")

    while True:
        time.sleep(POLL_INTERVAL)
        new_commit = get_latest_commit()
        if new_commit != last_commit:
            print(f"New commit detected: {new_commit}")
            trigger_rollout("nginx", "default")
            last_commit = new_commit

if __name__ == "__main__":
    main()
