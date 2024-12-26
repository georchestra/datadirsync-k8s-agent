#!/bin/bash
while true; do
    read -p "Define the namespace to map in your hosts file [default]: " namespace
    namespace=${namespace:-default}
    
    if [[ -n "$namespace" && "$namespace" =~ ^[a-zA-Z0-9-]+$ ]]; then
        break
    else
        echo "Error: Namespace must be a non-empty string containing only letters, numbers and hyphens"
    fi
done

kubectl get ingress --no-headers -n "$namespace" | awk '{printf("%s\t%s\n",$4,$3 )}' | sudo tee -a /etc/hosts