#!/bin/bash

# Loop to get valid namespace input
while true; do
    read -p "Define the namespace to use [default]: " namespace
    namespace=${namespace:-default}

    if [[ -n "$namespace" && "$namespace" =~ ^[a-zA-Z0-9-]+$ ]]; then
        break
    else
        echo "Error: Namespace must be a non-empty string containing only letters, numbers, and hyphens"
    fi
done

# Ask if the user wants to use an SSH key
read -p "Do you want to use an SSH key for Git access? (y/n): " use_ssh_key

# Default values file always used
helm_values_files="-f ./helm/values.yaml"

if [[ "$use_ssh_key" =~ ^[Yy]$ ]]; then
    values_ssh_file="./helm/values-ssh.yaml"
    if [ ! -f "$values_ssh_file" ]; then
        echo "Error: The file $values_ssh_file was not found."
        exit 1
    else
        echo "Using SSH key from $values_ssh_file."
        helm_values_files+=" -f $values_ssh_file"
    fi
    # Add the SSH repository path to the Helm command
    git_repo="git@github.com:jemacchi/nginx-site-test.git"
else
    # User does not want to use an SSH key, ask for username and token
    read -p "Enter Git username (leave empty for anonymous): " git_user
    read -p "Enter Git token (leave empty for anonymous): " git_token
fi

# Construct the Helm command
helm_cmd="helm install simple-git-rollout-operator ./helm --namespace \"$namespace\" --create-namespace $helm_values_files --set operator.namespaceName=\"$namespace\""

if [[ "$use_ssh_key" =~ ^[Yy]$ ]]; then
    helm_cmd="$helm_cmd --set repo.gitRepo=\"$git_repo\""
else
    # Add username and token to the Helm command if SSH key not provided
    if [ ! -z "$git_user" ]; then
        helm_cmd="$helm_cmd --set gitCredentials.username=\"$git_user\""
    fi

    if [ ! -z "$git_token" ]; then
        helm_cmd="$helm_cmd --set gitCredentials.token=\"$git_token\""
    fi
fi

# Execute the Helm command
echo "Executing Helm command: $helm_cmd"
eval $helm_cmd