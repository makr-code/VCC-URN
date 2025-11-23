# Kubernetes Deployment für VCC-URN Resolver

Dieses Verzeichnis enthält Kubernetes-Manifeste für das produktive Deployment des VCC-URN Resolvers.

## Dateien

- `configmap.yaml` - Konfiguration (ENV-Variablen)
- `secret.yaml` - Sensitive Daten (DB-Credentials, API-Keys)
- `deployment.yaml` - Deployment mit 2 Replicas, Probes, Resource Limits
- `service.yaml` - ClusterIP Service
- `hpa.yaml` - Horizontal Pod Autoscaler (2-10 Replicas)

## Voraussetzungen

- Kubernetes 1.28+
- PostgreSQL-Datenbank (extern oder als StatefulSet)
- Container Image: `vcc-urn-resolver:latest`

## Deployment

### 1. Secrets anpassen

**WICHTIG:** Bearbeite `secret.yaml` und ersetze die Beispielwerte:

```yaml
URN_DB_URL: "postgresql://urn:CHANGEME@postgres:5432/urn"
URN_API_KEYS: "your-secret-key:admin"
```

### 2. Image bauen und pushen

```bash
# Lokal bauen
docker build -t vcc-urn-resolver:latest .

# Oder zu Registry pushen
docker tag vcc-urn-resolver:latest your-registry/vcc-urn-resolver:latest
docker push your-registry/vcc-urn-resolver:latest
```

### 3. Manifeste anwenden

```bash
# ConfigMap und Secrets zuerst
kubectl apply -f deployment/k8s/configmap.yaml
kubectl apply -f deployment/k8s/secret.yaml

# Dann Deployment und Service
kubectl apply -f deployment/k8s/deployment.yaml
kubectl apply -f deployment/k8s/service.yaml

# Optional: HPA für Auto-Scaling
kubectl apply -f deployment/k8s/hpa.yaml
```

### 4. Status prüfen

```bash
# Pods prüfen
kubectl get pods -l app=vcc-urn-resolver

# Logs anzeigen
kubectl logs -l app=vcc-urn-resolver --tail=100 -f

# Service prüfen
kubectl get svc vcc-urn-resolver

# HPA Status
kubectl get hpa vcc-urn-resolver
```

## Zugriff

### Intern (innerhalb des Clusters)

```bash
curl http://vcc-urn-resolver:8000/healthz
```

### Extern (via Port-Forward)

```bash
kubectl port-forward svc/vcc-urn-resolver 8000:8000

# Dann lokal:
curl http://localhost:8000/
curl http://localhost:8000/metrics
```

### Extern (via Ingress - optional)

Erstelle ein Ingress-Objekt:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: vcc-urn-resolver
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: urn.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: vcc-urn-resolver
            port:
              number: 8000
```

## Monitoring

### Prometheus Metrics

Die App exponiert Metriken unter `/metrics`:

```bash
kubectl port-forward svc/vcc-urn-resolver 8000:8000
curl http://localhost:8000/metrics
```

Prometheus kann Pods automatisch scrapen via Annotations:

```yaml
prometheus.io/scrape: "true"
prometheus.io/port: "8000"
prometheus.io/path: "/metrics"
```

### Logs (JSON-Format)

Logs werden als JSON ausgegeben (siehe `URN_LOG_FORMAT=json` in ConfigMap):

```bash
kubectl logs -l app=vcc-urn-resolver --tail=100 | jq .
```

## Konfiguration anpassen

### ConfigMap bearbeiten

```bash
kubectl edit configmap vcc-urn-config
```

Nach Änderungen Pods neu starten:

```bash
kubectl rollout restart deployment vcc-urn-resolver
```

### Secrets bearbeiten

```bash
kubectl edit secret vcc-urn-secrets
```

**Hinweis:** Secrets sind Base64-kodiert. Zum Editieren:

```bash
echo -n "new-value" | base64
```

## Skalierung

### Manuell

```bash
kubectl scale deployment vcc-urn-resolver --replicas=5
```

### Automatisch (HPA)

HPA skaliert basierend auf CPU/Memory:
- Min: 2 Replicas
- Max: 10 Replicas
- Target CPU: 70%
- Target Memory: 80%

Status:

```bash
kubectl get hpa vcc-urn-resolver
```

## Troubleshooting

### Pods starten nicht

```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

Häufige Probleme:
- Image nicht gefunden → Image-Namen prüfen
- DB-Verbindung fehlgeschlagen → `URN_DB_URL` in Secret prüfen
- Probes schlagen fehl → Startup-Zeit erhöhen

### Readiness Probe schlägt fehl

Die `/readyz` Route prüft die DB-Verbindung. Wenn sie fehlschlägt:

```bash
# Pod-Logs prüfen
kubectl logs <pod-name>

# DB-Konnektivität testen
kubectl exec <pod-name> -- curl http://localhost:8000/readyz -v
```

### Metrics nicht sichtbar

Prüfe Prometheus-Scraping:

```bash
# Port-Forward und manuell testen
kubectl port-forward <pod-name> 8000:8000
curl http://localhost:8000/metrics
```

## Produktions-Checkliste

- [ ] Secrets mit echten Werten (nicht Beispiele)
- [ ] DB-URL auf produktive Datenbank zeigt
- [ ] Image-Tag auf spezifische Version (nicht `latest`)
- [ ] Resource Limits getestet
- [ ] HPA-Metriken validiert
- [ ] Ingress mit TLS konfiguriert
- [ ] Monitoring (Prometheus + Grafana) eingerichtet
- [ ] Logging (Loki/ELK) konfiguriert
- [ ] Backups für Postgres konfiguriert
- [ ] Disaster Recovery Plan dokumentiert

## Erweiterte Konfiguration

### Network Policies (optional)

Beschränke Netzwerk-Zugriff:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: vcc-urn-resolver
spec:
  podSelector:
    matchLabels:
      app: vcc-urn-resolver
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 53  # DNS
```

### Pod Disruption Budget (optional)

Stelle sicher, dass immer mindestens 1 Pod läuft:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: vcc-urn-resolver
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: vcc-urn-resolver
```

## Support

Bei Problemen siehe:
- [README.md](../../README.md) - Hauptdokumentation
- [complete-guide.md](../../docs/complete-guide.md) - Detaillierte Konfiguration
- [ROADMAP.md](../../docs/ROADMAP.md) - Entwicklungs-Roadmap
