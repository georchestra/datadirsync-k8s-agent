# datadirsync-k8s-agent

DatadirSync K8s Agent is a component that you can deploy on your Georchestra Kubernetes setup and it will monitor changes in a Git repository, triggering a rollout of a deployment based on those changes. This allows for a simple and automated way to deploy new versions of an application based on changes in a Git repository.

Important Notes: 

- The code of the agent interacts with K8s API in order to trigger a rollout of a deployment. It is not a full-fledged operator, but it is a simple agent that can be used to trigger a rollout of a deployment based on changes in a Git repository. Required Helm chart templates are in the scope of Georchestra Helm chart repository (https://github.com/georchestra/helm-georchestra/).

- It's not going to work in a non-K8s setup.

- Since it requires to interact with K8s API, it needs to be deployed in the same cluster where Georchestra is deployed along with permissions for Roles and RoleBindings, so you it's suggested not to use in a production environment (you are warned, use at your own risk. You will need to assign the agent roles for rolling out deployments !!!)

## Features

- Monitors changes in a Git repository
- Triggers a rollout of a deployment based on those changes
- Supports polling the Git repository at a configurable interval
- Supports specifying the Git repository URL, branch, and poll interval as environment variables
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

For a reference on how it's used in a Kubernetes deployment, see the [Georchestra Helm chart](https://github.com/georchestra/helm-georchestra) repository.

