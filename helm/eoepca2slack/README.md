# EOEPCA2Slack Helm Chart

A Helm chart for deploying the EOEPCA Slack notification function as a Knative Service.

## Description

This chart deploys a Knative Service for the EOEPCA Slack notification function, which receives CloudEvents and forwards them to Slack channels. The application runs as a serverless function with automatic scaling capabilities provided by Knative Serving.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- Knative Serving installed on the cluster

## Installation

### Add the Chart Repository (if applicable)

Add the EOEPCA Helm repository:

```bash
helm repo add eoepca https://your-repo-url
helm repo update
```

### Install from Local Directory

To install the chart directly from the local directory:

```bash
# Install with custom release name
helm install slack-notifications ./helm/eoepca2slack

# Install in a specific namespace
helm install slack-notifications ./helm/eoepca2slack --namespace eoepca --create-namespace
```

### Install with Custom Values

Create a custom values file:

```bash
# Create custom values
cat > my-values.yaml <<EOF
slack:
  webhookUrl: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  channel: "#eoepca-alerts"
  username: "EOEPCA Bot"

resources:
  requests:
    cpu: 200m
    memory: 256Mi
  limits:
    cpu: 1000m
    memory: 1Gi
EOF

# Install with custom values
helm install my-eoepca2slack ./helm/eoepca2slack -f my-values.yaml
```

## Configuration

### Slack Configuration

The chart supports two methods for configuring Slack credentials:

#### Method 1: Direct Configuration (Development)

Set Slack configuration directly in values:

```yaml
slack:
  webhookUrl: "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
  channel: "#alerts"
  username: "EOEPCA Bot"
  iconEmoji: ":satellite:"
```

#### Method 2: Secret Reference (Production)

Use Kubernetes secrets for sensitive data:

1. Create a secret:
```bash
kubectl create secret generic eoepca-slack-secret \
  --from-literal=webhook-url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL" \
  --from-literal=channel="#eoepca-alerts" \
  --from-literal=username="EOEPCA Bot" \
  --from-literal=icon-emoji=":satellite:"
```

2. Configure the chart to use the secret:
```yaml
slack:
  secretRef:
    enabled: true
    name: "eoepca-slack-secret"
    webhookUrlKey: "webhook-url"
    channelKey: "channel"
    usernameKey: "username"
    iconEmojiKey: "icon-emoji"
```

### Key Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `image.repository` | Container image repository | `ghcr.io/eoepca/send-notification-to-slack` |
| `image.tag` | Container image tag | `latest` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `slack.webhookUrl` | Slack webhook URL | `""` |
| `slack.channel` | Default Slack channel | `""` |
| `slack.username` | Bot username | `"EOEPCA Bot"` |
| `slack.iconEmoji` | Bot icon emoji | `":satellite:"` |
| `slack.secretRef.enabled` | Use secret for Slack config | `false` |
| `slack.secretRef.name` | Secret name | `"eoepca-slack-secret"` |
| `resources.requests.cpu` | CPU request | `100m` |
| `resources.requests.memory` | Memory request | `128Mi` |
| `resources.limits.cpu` | CPU limit | `500m` |
| `resources.limits.memory` | Memory limit | `512Mi` |
| `knative.visibility` | Service visibility (cluster-local or empty) | `"cluster-local"` |
| `knative.annotations` | Service-level annotations | `{}` |
| `knative.revisionAnnotations` | Revision-level annotations | `{}` |
| `knative.containerConcurrency` | Requests per container | `0` |
| `knative.timeoutSeconds` | Request timeout | `300` |

## Usage Examples

### Basic Installation

```bash
helm install eoepca2slack ./helm/eoepca2slack \
  --set slack.webhookUrl="https://hooks.slack.com/services/YOUR/WEBHOOK/URL" \
  --set slack.channel="#alerts"
```

### Production Installation with Secrets

```bash
# Create secret
kubectl create secret generic slack-config \
  --from-literal=webhook-url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Install chart
helm install eoepca2slack ./helm/eoepca2slack \
  --set slack.secretRef.enabled=true \
  --set slack.secretRef.name=slack-config
```


## Upgrading

To upgrade an existing release:

```bash
helm upgrade my-eoepca2slack ./helm/eoepca2slack
```

To upgrade with new values:

```bash
helm upgrade my-eoepca2slack ./helm/eoepca2slack -f my-values.yaml
```

## Uninstalling

To uninstall the chart:

```bash
helm uninstall my-eoepca2slack
```

This will remove all Kubernetes resources associated with the chart and delete the release.

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods -l app.kubernetes.io/name=eoepca2slack
```

### View Pod Logs

```bash
kubectl logs -l app.kubernetes.io/name=eoepca2slack
```

### Check Configuration

```bash
kubectl describe deployment <release-name>-eoepca2slack
```

### Verify Secret (if using secret reference)

```bash
kubectl get secret eoepca-slack-secret -o yaml
```

## Contributing

1. Make changes to the chart
2. Update the version in `Chart.yaml`
3. Test the chart: `helm lint ./helm/eoepca2slack`
4. Package the chart: `helm package ./helm/eoepca2slack`

## License

This chart is licensed under the same license as the EOEPCA project.
