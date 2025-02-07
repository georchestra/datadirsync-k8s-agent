#!/bin/bash
if [ -z "$1" ]; then
  echo "Uso: $0 <version>"
  exit 1
fi
VERSION="$1"
docker build -t georchestra/datadirsync-k8s-agent:$VERSION ./agent
