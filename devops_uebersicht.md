# DevOps, Observability und Delivery — eine Kurzübersicht

## DevOps als Arbeitsweise

DevOps ist keine Werkzeugsammlung, sondern eine Arbeitsweise, die Entwicklung und Betrieb enger verzahnt. Im Kern geht es um kurze Rückkopplungsschleifen, geteilte Verantwortung für Auslieferung und Betrieb sowie Automatisierung wiederkehrender Aufgaben. Teams, die DevOps leben, behandeln Zuverlässigkeit wie ein Produktmerkmal: sie messen sie, budgetieren sie und verbessern sie iterativ. 100-prozentige Verfügbarkeit ist weder realistisch noch wirtschaftlich — Zuverlässigkeit ist ein bewusster Trade-off zwischen Stabilität und Veränderungstempo.

Der DORA-Bericht 2024 zeigt, dass stabile Prioritäten sowohl die Produktivität als auch das Wohlbefinden schützen. KI-Werkzeuge beschleunigen den Entwickleralltag, können Stabilität und Durchsatz aber verschlechtern, wenn die Baseline unklar ist. Flexible Infrastruktur schlägt starre Cloud-Migration; Platform-Engineering hilft nur, wenn Teamautonomie gewahrt bleibt.

## SLOs, SLIs und Error Budgets

Ein Service Level Indicator ist eine nutzerrelevante Kennzahl wie Latenz, Fehlerrate oder Verfügbarkeit. Ein Service Level Objective setzt dafür ein Ziel über ein Zeitfenster, zum Beispiel 99,9 Prozent erfolgreicher Anfragen pro 30-Tage-Rolling-Window. Das Error Budget ist der zulässige Rest an Unzuverlässigkeit — er finanziert Produkt-Risiken wie Experimente und neue Features.

Alarme sollen aus Nutzerzielen abgeleitet werden, nicht aus willkürlichen Systemmetriken. Ein klassischer Fehler sind Alarme auf CPU-Auslastung, die keine Korrelation mit Nutzerfrust haben; stattdessen sollte man auf die SLIs alarmieren, die der SLO überwacht. Die Google-SRE-Books (Site Reliability Engineering, SRE Workbook) sind hier die kanonische Referenz, ergänzt um das Art-of-SLOs-Workshop-Material.

## Toil und Postmortems

Toil bezeichnet wiederkehrende, manuelle, nicht-skalierende operative Arbeit. Toil ist technisch und organisatorisch verschwendete Energie und muss sichtbar gemacht und systematisch abgebaut werden. Postmortems sind die strukturierte Auswertung von Vorfällen. Sie sind schuldfrei und fokussieren auf System- und Prozessverbesserung, nicht auf individuelle Sanktionen. Der Lifecycle eines Incidents reicht von Vorbereitung über Response und Mitigation bis Recovery und Postmortem.

## Git und Change-Flow

Git erlaubt billiges Branching, was Feature-Branches, Experimente und parallele Arbeitsstränge erst möglich macht. Im klassischen Pro-Git-Modell unterstützt verteiltes Git Pull-Request-Flows, Integrations-Branches und Maintainer-Workflows. GitHub Flow reduziert das auf kurze Branches mit beschreibenden Namen, kleinen isolierten Commits und Pull Requests als zentralen Review-Punkt. Status Checks und Branch-Protection erzwingen Qualität in der Pipeline.

## CI/CD und GitOps

GitHub Actions bietet event-getriebene Automatisierung: Jobs, Runner, Container, Artefakte, wiederverwendbare Workflows. Artifact Attestations liefern Provenance für Supply-Chain-Sicherheit. Für Kubernetes-native CI/CD sind Tekton und Argo CD relevant. Tekton modelliert Pipelines, Tasks und Trigger als Cluster-Ressourcen. Argo CD gleicht den gewünschten Zustand (Git) mit dem Ist-Zustand (Cluster) ab und reconciliert Differenzen. GitOps macht Git zur primären Steuerzentrale des Betriebs.

Jenkins bleibt relevant mit Declarative Pipelines und Multibranch Pipelines. Der Parallel Test Executor ist ein direkter Hebel gegen lange Feedback-Zyklen. Blue Ocean wird nicht mehr aktiv gepflegt und ist kein Ziel für Neueinführungen. Über alle Werkzeuge hinweg gilt OWASP CI/CD Security: signierte Commits, Least Privilege in SCM und Pipelines, keine hartkodierten Secrets, gehärtete Abhängigkeiten mit Pinning, Hash-Validierung und privaten Feeds.

## Container und Image-Supply-Chain

Docker abstrahiert Container als isolierte Prozesse, die sich den Host-Kernel teilen — leichter als VMs, aber mit geringerer Isolation. Der Lernpfad reicht von Installation über Build/Push über Dockerfiles, Layer, Multi-Stage-Builds, Ports und Volumes bis Compose. Podman ist die daemonlose, rootless-fähige Alternative mit nahezu identischer CLI. Buildah entkoppelt Image-Build von Runtime und unterstützt Rootless-Builds als First-Class-Feature.

Das OCI-Image-Format standardisiert Portabilität zwischen Tools und Registries. Harbor ist ein Open-Source-Registry mit Policies, RBAC, Vulnerability-Scans, Image-Signing und Replikation. OWASP Docker Security warnt vor geteiltem Host-Kernel, `/var/run/docker.sock`-Zugriff (≈ root), un-gescanten Images, fehlenden SBOMs und durch Docker publizierten Ports, die Host-Firewalls umgehen können.

## Infrastructure as Code

IaC wendet Software-Engineering-Praktiken auf Infrastruktur an. Thoughtworks-Empfehlungen: kleine, unabhängig änderbare Bausteine, kontinuierliches Testen und Delivery, Cloud-age-Governance statt Iron-age-Kontrolle. OpenTofu ist die offene Alternative im Terraform-Stil mit Modulen, State und Registry-Reuse. Ansible arbeitet desired-state: Control Node, Inventory, Managed Nodes, Modules, Playbooks. Operativ kommen Jinja2-Templating, Handlers, Loops, Delegation, Conditionals, Blocks und Error Handling hinzu. Ansible Builder und Runner standardisieren Execution Environments und trennen Ausführung von Kontrolle — relevant für CI/CD und Selbstbedienungsportale.

## Observability

Prometheus bietet pull-basiertes Metriken-Scraping auf HTTP-/metrics-Endpunkten; PromQL ist die Abfragesprache. Grafana vereint Dashboards, Log-Exploration, Annotationen und Managed Alerts in einem Workflow. Elastic Stack (Elasticsearch, Kibana, Beats, Elastic Agent, Logstash) ist stark bei Log- und Event-Ingestion; OpenSearch ist die Apache-2.0-Alternative für Suche und Analytics mit Security, Alerting und Index-Management.

Im LLM- und RAG-Kontext kommen spezielle Observability-Werkzeuge hinzu. Langfuse bietet Traces, Sessions, Scores und User-Feedback-Integration. Arize Phoenix ist die lokale Alternative mit LLM-Tracing, Online-Evals und Trace-Metrics (Token, Latenz, Kosten). Beide erlauben es, jede RAG-Interaktion als Trace mit Spans über Retrieval, Rerank, Prompt und Generation zu modellieren.

## FinOps

FinOps verzahnt Finance, Product und Engineering um eine gemeinsame Kosten-Signalbasis. Transparenz ist die erste Stufe: die größten Kostentreiber finden, dann systematisch Ineffizienzen angreifen. Typische Hebel sind Rightsizing, Speicher-Lifecycle, Abschalten ungenutzter Ressourcen via IaC, Container-Kostenzuordnung und Datentransfer-Optimierung. OpenCost liefert Kubernetes-Kostentransparenz in Echtzeit über `/allocation`- und `/assets`-APIs — Basis für Showback, Chargeback und Optimierung auf Namespace-, Cluster- und Ressourcen-Ebene. Die FOCUS-Spec standardisiert Kostendaten über Cloud-Anbieter hinweg und ist die Basis für Multi-Cloud-FinOps-Analyse.

## Security und Netzwerk

OpenSSH ist die Basisinfrastruktur für sicheren Remote-Zugriff und Automatisierung. WireGuard ist ein moderner, leichtgewichtiger VPN-Kern. nftables bildet die moderne Linux-Firewall-Grundlage. Keycloak übernimmt IAM und SSO, sobald DevOps über Deployments hinaus in Identitäten, Rollen und Zugriffe auf Services wächst. Im Anwendungsbereich bleibt die OWASP Top 10 die Referenz für wiederkehrende Schwachstellenklassen.

## Zusammenfassung

DevOps verlangt Disziplin in Messung, Automatisierung und Zusammenarbeit. Wer SLOs, Postmortems, Git, CI/CD, GitOps, Container, IaC, Observability, Security und FinOps als zusammengehörige Bausteine versteht, baut Systeme, die sich schnell ändern lassen, ohne unzuverlässig zu werden. Reliability, Sicherheit und Kosten sind dabei keine Nebenprodukte, sondern Produkteigenschaften — gemessen, budgetiert und iterativ verbessert.
