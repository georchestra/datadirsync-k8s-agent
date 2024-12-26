#!/bin/bash
while true; do
    read -p "Define the namespace to consider [default]: " namespace
    namespace=${namespace:-default}
    
    if [[ -n "$namespace" && "$namespace" =~ ^[a-zA-Z0-9-]+$ ]]; then
        break
    else
        echo "Error: Namespace must be a non-empty string containing only letters, numbers and hyphens"
    fi
done

helm uninstall simple-git-rollout-operator --namespace "$namespace"