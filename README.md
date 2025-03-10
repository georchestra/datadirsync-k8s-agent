# datadirsync-k8s-agent

DatadirSync K8s Agent is a component that can be deployed on your Georchestra Kubernetes setup to monitor changes in a Git repository and trigger a deployment rollout based on those changes. This provides a simple and automated approach to deploying new application versions when updates are made in a Git repository.

Important Notes:

- The agent's code interfaces with the K8s API to initiate a deployment rollout. It is not a complete operator but a straightforward agent to trigger deployments based on Git repository changes. Necessary Helm chart templates are part of the Georchestra Helm chart repository (https://github.com/georchestra/helm-georchestra/).

- It is inapplicable in a non-K8s environment.

- As it needs to interact with the K8s API, it must be deployed in the same cluster where Georchestra is hosted, with appropriate Roles and RoleBindings permissions. Caution is advised against using it in a production environment (use at your own risk, assigning agent roles is necessary for deploying rollouts !!!).

## Features

- Monitors changes in a Git repository
- Triggers a deployment rollout based on detected changes
- Supports configurable polling intervals for the Git repository
- Allows specifying Git repository URL, branch, and poll interval via environment variables
- Supports using a secret to store Git credentials

## Configuration

The agent will require to setup following environment variables:

- `GIT_REPO`: The URL of the Git repository to monitor (default: empty value, mandatory)
- `GIT_BRANCH`: The branch of the Git repository to monitor (default: `main`, mandatory)
- `POLL_INTERVAL`: The interval at which to poll the Git repository for changes (default: `60`)
- `GIT_USERNAME`: The username to use for Git authentication (optional)
- `GIT_TOKEN`: The token to use for Git authentication (optional) 
- `ROLLOUT_NAMESPACE`: The namespace of the deployment to rollout (default: `default`, mandatory)
- `GIT_SSH_COMMAND`: The SSH command to use for Git authentication (optional, when SSH keys used)
- `ROLLOUT_MAPPING_FILE`: The path to the YAML configuration file for deployment mappings (default: `/tmp/datadirsync/rollout_mapping_config.yaml`)

### Deployment Mapping

To configure mappings between files/folders and the deployments to be rolled out, a YAML configuration file must be specified. You can override the default file by creating a ConfigMap and setting the `ROLLOUT_MAPPING_FILE` environment variable.

Here is an example of how the YAML file might look:

```yaml
"*":
  - geoserver
"header":
  - header
"cas":
  - header
  - cas
```

In the example above:
- Changes within the `header` directory will trigger a rollout for the `header`.
- Changes within the `cas` directory will trigger a rollout for the `header` and `cas`.
- The wildcard `*` indicates that any changes will trigger rollouts for `geoserver`.

For a reference on how it's used in a Kubernetes deployment, see the [Georchestra Helm chart](https://github.com/georchestra/helm-georchestra) repository.