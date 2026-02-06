{{/*
Expand the name of the chart.
*/}}
{{- define "todo-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "todo-app.fullname" -}}
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
Create chart name and version as used by the chart label.
*/}}
{{- define "todo-app.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "todo-app.labels" -}}
helm.sh/chart: {{ include "todo-app.chart" . }}
{{ include "todo-app.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app: todo
{{- end }}

{{/*
Selector labels
*/}}
{{- define "todo-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Frontend labels
*/}}
{{- define "todo-app.frontend.labels" -}}
{{ include "todo-app.labels" . }}
component: frontend
{{- end }}

{{/*
Frontend selector labels
*/}}
{{- define "todo-app.frontend.selectorLabels" -}}
{{ include "todo-app.selectorLabels" . }}
component: frontend
{{- end }}

{{/*
Backend labels
*/}}
{{- define "todo-app.backend.labels" -}}
{{ include "todo-app.labels" . }}
component: backend
{{- end }}

{{/*
Backend selector labels
*/}}
{{- define "todo-app.backend.selectorLabels" -}}
{{ include "todo-app.selectorLabels" . }}
component: backend
{{- end }}

{{/*
MCP Server labels
*/}}
{{- define "todo-app.mcpServer.labels" -}}
{{ include "todo-app.labels" . }}
component: mcp-server
{{- end }}

{{/*
MCP Server selector labels
*/}}
{{- define "todo-app.mcpServer.selectorLabels" -}}
{{ include "todo-app.selectorLabels" . }}
component: mcp-server
{{- end }}

{{/*
AI Agent labels
*/}}
{{- define "todo-app.aiAgent.labels" -}}
{{ include "todo-app.labels" . }}
component: ai-agent
{{- end }}

{{/*
AI Agent selector labels
*/}}
{{- define "todo-app.aiAgent.selectorLabels" -}}
{{ include "todo-app.selectorLabels" . }}
component: ai-agent
{{- end }}

{{/*
Secret name
*/}}
{{- define "todo-app.secretName" -}}
{{ include "todo-app.fullname" . }}-secrets
{{- end }}

{{/*
ConfigMap name
*/}}
{{- define "todo-app.configMapName" -}}
{{ include "todo-app.fullname" . }}-config
{{- end }}
