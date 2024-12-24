#!/bin/bash
kubectl get ingress --no-headers -n default | awk '{printf("%s\t%s\n",$4,$3 )}' | sudo tee -a /etc/hosts
