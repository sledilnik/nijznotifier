{{/*
Expand the name of the chart.
*/}}
{{- define "nijznotifier.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "nijznotifier.fullname" -}}
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
{{- define "nijznotifier.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "nijznotifier.labels" -}}
helm.sh/chart: {{ include "nijznotifier.chart" . }}
{{ include "nijznotifier.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "nijznotifier.selectorLabels" -}}
app.kubernetes.io/name: {{ include "nijznotifier.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Expand the name of the chart.
*/}}
{{- define "nijznotifier.pvc" -}}
{{- $fullName := include "nijznotifier.fullname" . -}}
{{- default (printf "%s-data" $fullName ) .Values.persistence.existingClaim }}
{{- end }}


{{/*
Expand the name of the chart.
*/}}
{{- define "nijznotifier.secret" -}}
{{- $fullName := include "nijznotifier.fullname" . -}}
{{- default (printf "%s" $fullName ) .Values.existingSecret }}
{{- end }}