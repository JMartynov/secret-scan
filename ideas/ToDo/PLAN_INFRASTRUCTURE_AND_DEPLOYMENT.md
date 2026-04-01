# Task: Infrastructure & Cloud Deployment (IaC)

## 1. Objective & Context
*   **Goal**: Define the production infrastructure as code for scalable, secure deployment on AWS/GCP.
*   **Rationale**: To ensure consistent, reproducible environments and support enterprise-grade availability.
*   **Files Affected**:
    *   `Dockerfile` (Containerization)
    *   `docker-compose.yml` (Local dev)
    *   `infra/terraform/` (IaC definitions)
    *   `.github/workflows/deploy.yml` (CI/CD)

## 2. Research & Strategy
*   **Cloud**: AWS (ECS Fargate/RDS) or GCP (Cloud Run/Cloud SQL).
*   **Security**: Private subnets, VPC isolation, and encrypted DB volumes.
*   **Scaling**: Autoscaling based on CPU/Request count.

## 3. Implementation Checklist
- [ ] **Production Dockerfile**: Optimized, multi-stage build for the FastAPI app.
- [ ] **Terraform Modules**: Define VPC, ECS Cluster, RDS Instance, and Redis Cache.
- [ ] **CI/CD Pipeline**: Automate image building, pushing to ECR/GCR, and updating ECS/Cloud Run.
- [ ] **Monitoring**: Setup CloudWatch/Stackdriver alerts for system health.
- [ ] **Secret Management**: Use AWS Secrets Manager or GCP Secret Manager for API keys and DB creds.

## 4. Testing & Verification (Mandatory)
### 4.1 Infrastructure Testing
- [ ] Run `terraform plan` to verify resource creation.
- [ ] Perform a "Dry Run" deployment in a staging environment.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: The API service is reachable via a load balancer over HTTPS.
- [ ] **Scenario**: The system automatically scales up during a high-volume scanning load.
- [ ] **Scenario**: Database failover works as expected without data loss.

## 5. Demo & Documentation
- [ ] **Deployment Guide**: Internal documentation on how to rotate secrets and update infrastructure.
- [ ] **Architecture Diagram**: Visual representation of the cloud stack.

## 6. Engineering Standards
*   **Principle of Least Privilege**: Ensure IAM roles have the minimum permissions required.
*   **Cost Efficiency**: Use Fargate/Cloud Run to avoid paying for idle compute.
