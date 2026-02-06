# AI-Assisted Infra Debugging Skill

## Purpose
Diagnose infrastructure issues using kubectl-ai + kagent outputs to identify root causes and recommend fixes.

## Capabilities

### 1. Read Pod Logs & Events
- **Pod logs**: Extract recent logs from running/crashed containers
- **Previous logs**: Retrieve logs from previous container instances (`--previous`)
- **Events**: Kubernetes events for pods, deployments, nodes
- **Describe output**: Full resource state and conditions

```bash
# Common diagnostic commands
kubectl logs <pod> [-c container] [--previous]
kubectl describe pod <pod>
kubectl get events --field-selector involvedObject.name=<pod>
kubectl get events --sort-by='.lastTimestamp'
```

### 2. Correlate Failures

#### CrashLoopBackOff
| Symptom | Likely Cause | Investigation |
|---------|--------------|---------------|
| Exit code 1 | Application error | Check logs for stack trace |
| Exit code 137 | OOMKilled | Check memory limits, increase resources |
| Exit code 143 | SIGTERM | Graceful shutdown issue, check preStop hooks |
| Immediate crash | Missing config/secret | Check env vars, mounted volumes |
| Crash after start | Probe failure | Check liveness probe settings |

#### ImagePullBackOff
| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| "unauthorized" | Missing imagePullSecret | Add/fix registry credentials |
| "not found" | Wrong image name/tag | Verify image exists in registry |
| "timeout" | Network/registry issue | Check network policies, DNS |
| "manifest unknown" | Tag doesn't exist | Use valid tag, check registry |

#### Other Common Failures
| Status | Description | Investigation |
|--------|-------------|---------------|
| Pending | Scheduling failed | Check node resources, affinity, taints |
| ContainerCreating | Volume/network setup | Check PVC, CSI driver, CNI |
| Init:Error | Init container failed | Check init container logs |
| Evicted | Node pressure | Check node conditions, resource usage |
| Unknown | Node unreachable | Check node status, kubelet |

### 3. Suggest Minimal Corrective Action
- **Principle**: Smallest change that fixes the issue
- **Validation**: Verify fix doesn't introduce new issues
- **Rollback**: Always provide rollback steps

## Output Format

### Root Cause Analysis
```markdown
## Root Cause

**Issue**: [Brief description of the failure]
**Category**: [CrashLoopBackOff | ImagePullBackOff | Pending | OOMKilled | etc.]
**Affected Resource**: [pod/deployment/service name]
**Evidence**:
- Log snippet: `[relevant log line]`
- Event: `[relevant Kubernetes event]`
- Metric: [resource usage if applicable]
```

### Fix Recommendation
```markdown
## Recommended Fix

**Action**: [Specific action to take]
**Impact**: [What this change affects]
**Risk Level**: [Low | Medium | High]

### Steps
1. [Step 1]
2. [Step 2]
3. [Verification step]

### Rollback
1. [How to undo if needed]
```

### Confidence Level
```markdown
## Confidence Assessment

**Level**: [High | Medium | Low]
**Reasoning**: [Why this confidence level]

- High (>80%): Clear evidence, common pattern, verified similar fixes
- Medium (50-80%): Partial evidence, multiple possible causes
- Low (<50%): Inconclusive, needs more investigation
```

## Diagnostic Workflows

### CrashLoopBackOff Workflow
```
1. Get pod status
   kubectl get pod <name> -o wide

2. Check recent events
   kubectl describe pod <name> | grep -A 10 Events

3. Get current logs
   kubectl logs <name> --tail=100

4. Get previous container logs (if restarted)
   kubectl logs <name> --previous --tail=100

5. Check resource usage
   kubectl top pod <name>

6. Analyze exit code
   kubectl get pod <name> -o jsonpath='{.status.containerStatuses[0].state.terminated.exitCode}'
```

### ImagePullBackOff Workflow
```
1. Check image name and tag
   kubectl get pod <name> -o jsonpath='{.spec.containers[*].image}'

2. Verify imagePullSecrets
   kubectl get pod <name> -o jsonpath='{.spec.imagePullSecrets}'

3. Test registry access
   kubectl run test --image=<image> --rm -it --restart=Never -- echo "success"

4. Check secret exists and is valid
   kubectl get secret <pull-secret> -o yaml
```

### Pending Pod Workflow
```
1. Check scheduling status
   kubectl describe pod <name> | grep -A 5 "Conditions"

2. Check node resources
   kubectl describe nodes | grep -A 5 "Allocated resources"

3. Check taints and tolerations
   kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints

4. Check affinity rules
   kubectl get pod <name> -o jsonpath='{.spec.affinity}'
```

## kagent Integration

### Cluster Health Analysis
```bash
# Get cluster health summary
kagent analyze cluster

# Check resource utilization
kagent analyze resources

# Get optimization recommendations
kagent recommend
```

### Interpreting kagent Output
| kagent Signal | Meaning | Action |
|---------------|---------|--------|
| CPU throttling | Pods hitting CPU limits | Increase CPU limits or optimize code |
| Memory pressure | Approaching OOM | Increase memory or fix leaks |
| Pending pods | Insufficient cluster capacity | Scale cluster or reduce requests |
| Failed probes | Health check failures | Fix application or adjust probe settings |
| Restart loops | Repeated crashes | Investigate root cause in logs |

## Common Fix Patterns

### Resource Issues
```yaml
# Increase memory limit
resources:
  limits:
    memory: "512Mi"  # was 256Mi
  requests:
    memory: "256Mi"
```

### Probe Adjustments
```yaml
# Increase probe tolerance for slow startup
livenessProbe:
  initialDelaySeconds: 60  # was 10
  periodSeconds: 10
  failureThreshold: 6      # was 3
```

### Image Pull Fix
```yaml
# Add imagePullSecrets
spec:
  imagePullSecrets:
    - name: registry-credentials
```

### Environment Fix
```yaml
# Add missing required env var
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: app-secrets
        key: database-url
```

## Escalation Criteria

When to escalate to human operator:
- **Confidence < 50%**: Need more context or investigation
- **Data loss risk**: Any action that could lose data
- **Production impact**: Changes affecting live traffic
- **Security concerns**: Potential security implications
- **Cluster-wide issues**: Problems affecting multiple namespaces
- **Infrastructure changes**: Node-level or cluster-level modifications

## Quick Reference

### Exit Codes
| Code | Signal | Meaning |
|------|--------|---------|
| 0 | - | Success |
| 1 | - | General error |
| 126 | - | Permission denied |
| 127 | - | Command not found |
| 128+n | Signal n | Terminated by signal |
| 137 | SIGKILL (9) | OOMKilled or forced termination |
| 143 | SIGTERM (15) | Graceful termination |

### Pod Conditions
| Condition | Meaning |
|-----------|---------|
| PodScheduled | Pod assigned to node |
| Initialized | Init containers completed |
| ContainersReady | All containers ready |
| Ready | Pod ready to serve traffic |
