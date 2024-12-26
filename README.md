# simple-git-rollout-operator

Simple Git Rollout Operator is a Kubernetes operator that monitors changes in a Git repository and triggers a rollout of a deployment based on those changes. This allows for a simple and automated way to deploy new versions of an application based on changes in a Git repository (not necessarily the same repository which contains the templates for the deployment).

## Features

- Monitors changes in a Git repository
- Triggers a rollout of a deployment based on those changes
- Supports polling the Git repository at a configurable interval
- Supports specifying the Git repository URL, branch, and poll interval as environment variables
- Supports using a secret to store Git credentials

## Installation

To install the Simple Git Rollout Operator, you can use the provided Helm chart.

Execute the following command to install the operator and an Nginx server which is updated based on Git repo changes:

'''
./start-demo.sh
'''

This command starts an interactive script that:

1. Prompts for a Kubernetes namespace (defaults to "default")
   - Validates the namespace only contains letters, numbers and hyphens
   - Repeats prompt if input is invalid

2. Prompts for a Git username (optional)
   - Can be left empty for anonymous access

3. Prompts for a Git token (optional)
   - Can be left empty for anonymous access

4. Installs the simple-git-rollout-operator using Helm:
   - Installs it in the specified namespace
   - Creates the namespace if it doesn't exist
   - Configures Git credentials if provided
   
## Configuration

The following configuration options are available for the Simple Git Rollout Operator:

- `operator.image`: The Docker image for the operator (default: `jemacchi/simple-git-rollout-operator:1.1`)
- `operator.gitRepo`: The URL of the Git repository to monitor (default: `https://github.com/jemacchi/simple-git-rollout-operator-nginx-demo.git`)
- `operator.gitBranch`: The branch of the Git repository to monitor (default: `main`)
- `operator.pollInterval`: The interval at which to poll the Git repository for changes (default: `60`)
- `nginx.image`: The Docker image for the Nginx server (default: `nginx:1.23.1`)
- `nginx.gitRepo`: The URL of the Git repository containing the Nginx configuration (default: `https://github.com/jemacchi/simple-git-rollout-operator-nginx-demo.git`)
- `nginx.gitBranch`: The branch of the Git repository containing the Nginx configuration (default: `main`)








