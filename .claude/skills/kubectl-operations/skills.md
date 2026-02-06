# Kubectl Operations Skill

## Purpose
Execute Kubernetes cluster operations including deployments, scaling, debugging, and service management with safety-first practices.

## Capabilities

### 1. Resource Management
- **Create/Apply**: Deploy resources from manifests
- **Update**: Modify existing resources
- **Delete**: Remove resources with safety checks
- **Patch**: Targeted updates to specific fields

### 2. Workload Operations
- **Deployments**: Rollouts, rollbacks, scaling
- **Pods**: Exec, logs, port-forward, debug
- **Jobs/CronJobs**: Run, suspend, trigger

### 3. Service & Networking
- **Services**: Expose, modify, troubleshoot
- **Ingress**: Configure routing rules
- **Network Policies**: Inspect connectivity

### 4. Configuration
- **ConfigMaps**: Create, update, mount
- **Secrets**: Manage sensitive data
- **Resource Quotas**: View and manage limits

## Core Commands Reference

### Context & Namespace Management
```bash
# View current context
kubectl config current-context

# List all contexts
kubectl config get-contexts

# Switch context
kubectl config use-context <context-name>

# Set default namespace
kubectl config set-context --current --namespace=<namespace>

# View all namespaces
kubectl get namespaces
```

### Resource Viewing
```bash
# List resources (common patterns)
kubectl get pods [-n namespace] [-o wide|yaml|json]
kubectl get deployments
kubectl get services
kubectl get ingress
kubectl get all

# Describe resource (detailed info)
kubectl describe pod <name>
kubectl describe deployment <name>
kubectl describe node <name>

# Get resource YAML
kubectl get pod <name> -o yaml

# Watch resources
kubectl get pods -w

# Get resources across all namespaces
kubectl get pods -A
```

### Deployment Operations
```bash
# Create deployment
kubectl create deployment <name> --image=<image>

# Apply manifest
kubectl apply -f deployment.yaml

# Update image
kubectl set image deployment/<name> <container>=<image>

# Scale deployment
kubectl scale deployment <name> --replicas=<count>

# Rollout status
kubectl rollout status deployment/<name>

# Rollout history
kubectl rollout history deployment/<name>

# Rollback to previous
kubectl rollout undo deployment/<name>

# Rollback to specific revision
kubectl rollout undo deployment/<name> --to-revision=<n>

# Pause/Resume rollout
kubectl rollout pause deployment/<name>
kubectl rollout resume deployment/<name>

# Restart deployment (rolling restart)
kubectl rollout restart deployment/<name>
```

### Pod Operations
```bash
# Get pod logs
kubectl logs <pod> [-c container] [-f] [--tail=100]

# Get previous container logs
kubectl logs <pod> --previous

# Execute command in pod
kubectl exec -it <pod> -- /bin/sh
kubectl exec <pod> -- <command>

# Copy files to/from pod
kubectl cp <pod>:/path/to/file ./local/path
kubectl cp ./local/file <pod>:/path/to/dest

# Port forward
kubectl port-forward pod/<name> <local>:<remote>
kubectl port-forward svc/<name> <local>:<remote>

# Debug pod (ephemeral container)
kubectl debug <pod> -it --image=busybox

# Run temporary pod
kubectl run debug --image=busybox --rm -it --restart=Never -- sh
```

### Service Operations
```bash
# Expose deployment as service
kubectl expose deployment <name> --port=<port> --target-port=<target>

# Create service types
kubectl expose deployment <name> --type=ClusterIP --port=80
kubectl expose deployment <name> --type=NodePort --port=80
kubectl expose deployment <name> --type=LoadBalancer --port=80

# Get service endpoints
kubectl get endpoints <service>

# Test service DNS
kubectl run test --image=busybox --rm -it --restart=Never -- nslookup <service>
```

### ConfigMap & Secret Operations
```bash
# Create ConfigMap from literal
kubectl create configmap <name> --from-literal=key=value

# Create ConfigMap from file
kubectl create configmap <name> --from-file=config.properties

# Create Secret from literal
kubectl create secret generic <name> --from-literal=password=secret

# Create Secret from file
kubectl create secret generic <name> --from-file=credentials.json

# View Secret (base64 decoded)
kubectl get secret <name> -o jsonpath='{.data.password}' | base64 -d
```

### Resource Management
```bash
# Delete resource
kubectl delete pod <name>
kubectl delete -f manifest.yaml

# Delete with grace period
kubectl delete pod <name> --grace-period=0 --force

# Label resources
kubectl label pod <name> env=production
kubectl label pod <name> env-  # remove label

# Annotate resources
kubectl annotate pod <name> description="my pod"

# Patch resource
kubectl patch deployment <name> -p '{"spec":{"replicas":3}}'
```

## Safety Practices

### Pre-Operation Checks
```bash
# Always verify context before destructive operations
kubectl config current-context

# Dry-run before apply
kubectl apply -f manifest.yaml --dry-run=client
kubectl apply -f manifest.yaml --dry-run=server

# Diff before apply
kubectl diff -f manifest.yaml
```

### Safe Delete Patterns
```bash
# Delete with confirmation (list first)
kubectl get pods -l app=myapp
kubectl delete pods -l app=myapp

# Never use without namespace awareness
kubectl delete pods --all  # DANGEROUS without -n

# Safer: always specify namespace
kubectl delete pods --all -n <namespace>
```

### Rollback Readiness
```bash
# Before updates, note current state
kubectl get deployment <name> -o yaml > backup.yaml

# Check rollout history exists
kubectl rollout history deployment/<name>

# After issues, rollback immediately
kubectl rollout undo deployment/<name>
```

## Troubleshooting Patterns

### Pod Not Starting
```bash
# 1. Check pod status
kubectl get pod <name> -o wide

# 2. Describe for events
kubectl describe pod <name>

# 3. Check logs (if container started)
kubectl logs <name>

# 4. Check previous logs (if restarted)
kubectl logs <name> --previous

# 5. Check node status
kubectl describe node <node-name>
```

### Service Not Accessible
```bash
# 1. Verify service exists and has endpoints
kubectl get svc <name>
kubectl get endpoints <name>

# 2. Check pod labels match service selector
kubectl get pods --show-labels
kubectl get svc <name> -o jsonpath='{.spec.selector}'

# 3. Test from within cluster
kubectl run test --image=busybox --rm -it --restart=Never -- wget -qO- http://<service>:<port>

# 4. Check network policies
kubectl get networkpolicies
```

### High Resource Usage
```bash
# Check pod resource usage
kubectl top pods [-n namespace]

# Check node resource usage
kubectl top nodes

# Get resource requests/limits
kubectl describe pod <name> | grep -A 3 "Limits\|Requests"

# Find pods without limits
kubectl get pods -o json | jq '.items[] | select(.spec.containers[].resources.limits == null) | .metadata.name'
```

## Minikube-Specific Operations

```bash
# Start/stop cluster
minikube start [--driver=docker|hyperv]
minikube stop
minikube delete

# Access dashboard
minikube dashboard

# Get service URL
minikube service <name> --url

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server
minikube addons list

# Load local image
minikube image load <image>:<tag>

# SSH into node
minikube ssh

# Tunnel for LoadBalancer services
minikube tunnel
```

## Output Formatting

### JSONPath Queries
```bash
# Get pod IPs
kubectl get pods -o jsonpath='{.items[*].status.podIP}'

# Get container images
kubectl get pods -o jsonpath='{.items[*].spec.containers[*].image}'

# Get node names
kubectl get nodes -o jsonpath='{.items[*].metadata.name}'

# Custom columns
kubectl get pods -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,IP:.status.podIP
```

### Filtering
```bash
# By label
kubectl get pods -l app=myapp
kubectl get pods -l 'app in (web,api)'

# By field
kubectl get pods --field-selector status.phase=Running
kubectl get pods --field-selector spec.nodeName=node1

# By namespace
kubectl get pods -n kube-system
kubectl get pods -A  # all namespaces
```

## Quick Reference

### Resource Short Names
| Full Name | Short | Example |
|-----------|-------|---------|
| pods | po | `kubectl get po` |
| deployments | deploy | `kubectl get deploy` |
| services | svc | `kubectl get svc` |
| configmaps | cm | `kubectl get cm` |
| secrets | - | `kubectl get secrets` |
| namespaces | ns | `kubectl get ns` |
| nodes | no | `kubectl get no` |
| persistentvolumeclaims | pvc | `kubectl get pvc` |
| ingresses | ing | `kubectl get ing` |
| replicasets | rs | `kubectl get rs` |

### Common Flags
| Flag | Purpose |
|------|---------|
| `-n` | Specify namespace |
| `-A` | All namespaces |
| `-o wide` | More columns |
| `-o yaml` | YAML output |
| `-o json` | JSON output |
| `-w` | Watch mode |
| `-l` | Label selector |
| `--dry-run=client` | Preview without executing |
| `-f` | From file |
| `--force` | Force operation |

### Dangerous Commands (Use with Caution)
| Command | Risk | Safer Alternative |
|---------|------|-------------------|
| `kubectl delete pods --all` | Deletes all pods | Add `-n namespace` |
| `kubectl delete ns <name>` | Deletes everything in namespace | List contents first |
| `kubectl apply -f .` | Applies all YAML in directory | Review files first |
| `kubectl edit` | Direct cluster edits | Use `apply -f` with version control |
| `kubectl exec` without `-it` | May hang | Always use `-it` for shells |
