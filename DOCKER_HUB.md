# Quick reference

-    **Maintained by**:  
      [georchestra.org](https://www.georchestra.org/)

-    **Where to get help**:  
     the [datadirsync-k8s-agent Github repo](https://github.com/georchestra/datadirsync-k8s-agent), [IRC chat](https://matrix.to/#/#georchestra:osgeo.org), Stack Overflow

# Featured tags

- `latest`, `1.3.1`

# Quick reference

-	**Where to file issues**:  
     [https://github.com/georchestra/datadirsync-k8s-agent/issues](https://github.com/georchestra/datadirsync-k8s-agent/issues)

-	**Supported architectures**:   
     [`amd64`](https://hub.docker.com/r/amd64/docker/)

-	**Source of this description**:  
     [docs repo's `datadirsync-k8s-agent/` directory](https://github.com/georchestra/datadirsync-k8s-agent/blob/main/DOCKER_HUB.md)

# What is `georchestra/datadirsync-k8s-agent`

**Datadirsync-k8s-agent** is a sidecar container that used in context of a geOrchestra Kubernetes setup allows to monitor changes in a Git repository, triggering a rollout of a deployment based on those changes. 

# How to use this image

For this specific component, see the `datadirsync` folder in the [`Helm Georchestra repository`](https://github.com/georchestra/helm-georchestra/tree/main/templates) and the section `datadirsync` in the [`values.yaml`](https://github.com/georchestra/helm-georchestra/blob/main/values.yaml) file.

## Where is it built

This image is built using docker. You can see details in the Dockerfile in the `agent´ folder.

# License

View [license information](https://www.georchestra.org/software.html) for the software contained in this image.

As with all Docker images, these likely also contain other software which may be under other licenses (such as Bash, etc from the base distribution, along with any direct or indirect dependencies of the primary software being contained).

[//]: # (Some additional license information which was able to be auto-detected might be found in [the `repo-info` repository's georchestra/ directory]&#40;&#41;.)

As for any docker image, it is the user's responsibility to ensure that usages of this image comply with any relevant licenses for all software contained within.
