# Helm Chart Generation Skill

## Purpose
Generate production-ready Helm charts from application specifications and Kubernetes manifests.

## Capabilities

### 1. Chart Structure Generation
- **Chart.yaml**: Metadata, versioning, dependencies
- **values.yaml**: Configurable parameters with sensible defaults
- **templates/**: Kubernetes manifest templates with Helm templating
- **helpers.tpl**: Reusable template functions and naming conventions

### 2. Template Generation
- **Deployment**: Replicas, containers, probes, resources
- **Service**: ClusterIP, NodePort, LoadBalancer configurations
- **Ingress**: Host rules, TLS, annotations for ingress controllers
- **ConfigMap/Secret**: Application configuration externalization
- **HPA**: Horizontal Pod Autoscaler for scaling policies
- **PVC**: Persistent Volume Claims for stateful needs
- **ServiceAccount**: RBAC and pod identity

### 3. Values Management
- **Environment-specific overrides**: dev, staging, production
- **Nested values**: Organized by component/concern
- **Documentation**: Inline comments explaining each value
- **Type safety**: Proper defaults and validation

### 4. Best Practices Enforcement
- **Naming conventions**: Consistent resource naming with release context
- **Labels and annotations**: Standard Kubernetes labels (app, version, component)
- **Security contexts**: Non-root, read-only filesystem defaults
- **Resource limits**: CPU/memory requests and limits

## Output

### Chart Structure
```
mychart/
├── Chart.yaml
├── values.yaml
├── values-dev.yaml
├── values-prod.yaml
├── templates/
│   ├── _helpers.tpl
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── hpa.yaml
│   ├── pvc.yaml
│   ├── serviceaccount.yaml
│   └── NOTES.txt
└── .helmignore
```

### Example Chart.yaml
```yaml
apiVersion: v2
name: myapp
description: A Helm chart for MyApp
type: application
version: 0.1.0
appVersion: "1.0.0"
keywords:
  - myapp
  - backend
maintainers:
  - name: Team
    email: team@example.com
```

### Example values.yaml
```yaml
replicaCount: 3

image:
  repository: myapp
  tag: "1.0.0"
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80
  targetPort: 8080

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: myapp.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: myapp-tls
      hosts:
        - myapp.example.com

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80

env:
  DATABASE_URL: ""
  LOG_LEVEL: "info"

secrets:
  create: true
  data: {}
```

### Example _helpers.tpl
```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "myapp.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "myapp.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "myapp.labels" -}}
helm.sh/chart: {{ include "myapp.chart" . }}
{{ include "myapp.selectorLabels" . }}
app.kubernetes.io/version: {{ .Values.image.tag | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "myapp.selectorLabels" -}}
app.kubernetes.io/name: {{ include "myapp.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

## Warnings for Anti-Patterns

### Chart Anti-Patterns
- Hardcoded values in templates (use values.yaml)
- Missing helper templates for common patterns
- No NOTES.txt for post-install instructions
- Inconsistent naming across resources
- Missing chart version increments on changes

### Values Anti-Patterns
- Deeply nested values (keep it 2-3 levels max)
- No default values for required fields
- Missing comments/documentation
- Environment-specific values in base values.yaml
- Secrets stored in plain text in values

### Template Anti-Patterns
- Not using `include` for reusable snippets
- Missing `toYaml` with proper indentation
- Hardcoded namespaces (should use Release.Namespace)
- No conditional blocks for optional resources
- Missing quotes around string values with special chars

## Generation Checklist

- [ ] Chart.yaml has correct apiVersion, name, version, appVersion
- [ ] values.yaml has sensible defaults for all configurable options
- [ ] _helpers.tpl defines name, fullname, labels, selectorLabels
- [ ] All templates use helpers for naming consistency
- [ ] Resources have proper labels and annotations
- [ ] Probes configured (liveness, readiness, startup if needed)
- [ ] Resource requests and limits defined
- [ ] Security context set (non-root, read-only rootfs)
- [ ] Ingress template handles TLS correctly
- [ ] NOTES.txt provides useful post-install info
- [ ] values-{env}.yaml files for environment overrides
- [ ] helm lint passes without errors
- [ ] helm template renders valid YAML

## Common Helm Functions

| Function | Purpose | Example |
|----------|---------|---------|
| `include` | Include named template | `{{ include "app.name" . }}` |
| `toYaml` | Convert to YAML | `{{ toYaml .Values.env \| nindent 12 }}` |
| `default` | Provide default value | `{{ default "nginx" .Values.image }}` |
| `quote` | Quote string | `{{ .Values.name \| quote }}` |
| `required` | Fail if missing | `{{ required "name required" .Values.name }}` |
| `tpl` | Render string as template | `{{ tpl .Values.config . }}` |
| `lookup` | Query cluster | `{{ lookup "v1" "Secret" "ns" "name" }}` |

## Minikube Compatibility

### Considerations
- Use `NodePort` or `LoadBalancer` with `minikube tunnel`
- Enable ingress addon: `minikube addons enable ingress`
- Use `minikube service <name>` to access services
- Local image loading: `minikube image load <image>`
- Storage class: `standard` (default provisioner)

### values-minikube.yaml Example
```yaml
service:
  type: NodePort
  nodePort: 30080

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: myapp.local
      paths:
        - path: /
          pathType: Prefix

resources:
  requests:
    cpu: 50m
    memory: 64Mi
  limits:
    cpu: 200m
    memory: 128Mi
```
