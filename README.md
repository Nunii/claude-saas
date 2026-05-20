# claude-saas

A multi-tenant LLM chatbot API. Built as the capstone for senior DevOps training.

## What it does

- HTTP REST API for chat with Claude
- Persists conversation history in Postgres
- Multi-tenant by design (tenant_id on every conversation)
- Will grow: RAG, vector DB, K8s, observability, signing, multi-region

## Local dev

Prereqs: Docker, Docker Compose, an Anthropic API key.

\`\`\`bash
# Set your API key (don't commit this file!)
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

# Start everything
cd deploy
docker compose --env-file ../.env up --build

# Test it
curl -X POST http://localhost:8000/v1/chat \
  -H 'Content-Type: application/json' \
  -d '{"message": "Hello!"}'
\`\`\`

## Project structure

\`\`\`
services/api/   FastAPI service
deploy/         docker-compose, helm charts (later)
docs/           architecture, ADRs, runbooks
\`\`\`

## Roadmap

- [x] Module 2: Containerized FastAPI + Postgres
- [ ] Module 3: Networking deep-dive applied to request path
- [ ] Module 4: Deploy to Kubernetes (kind, then EKS)
- [ ] Module 5: AWS infrastructure (VPC, EKS, RDS, IRSA)
- [ ] Module 6: All infra as Terraform modules
- [ ] Module 7: CI/CD with GitHub Actions + OIDC + cosign
- [ ] Module 8: Observability (Prometheus, Loki, Tempo, SLOs)
- [ ] Module 9: Security (Kyverno, Falco, mTLS)
- [ ] Module 10: RAG + LiteLLM + eval pipelines + self-hosted Llama
