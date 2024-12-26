#!/bin/bash
while true; do
    read -p "Define the namespace to use [default]: " namespace
    namespace=${namespace:-default}
    
    if [[ -n "$namespace" && "$namespace" =~ ^[a-zA-Z0-9-]+$ ]]; then
        break
    else
        echo "Error: Namespace must be a non-empty string containing only letters, numbers and hyphens"
    fi
done

read -p "Enter Git username (leave empty for anonymous): " git_user
read -p "Enter Git token (leave empty for anonymous): " git_token

helm_cmd="helm install simple-git-rollout-operator ./helm --namespace \"$namespace\" --create-namespace --set operator.namespaceName=\"$namespace\""

if [ ! -z "$git_user" ]; then
    helm_cmd="$helm_cmd --set gitCredentials.username=\"$git_user\""
fi

if [ ! -z "$git_token" ]; then
    helm_cmd="$helm_cmd --set gitCredentials.token=\"$git_token\""
fi

echo "Executing Helm command: $helm_cmd"
eval $helm_cmd