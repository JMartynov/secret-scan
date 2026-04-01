# Task: Infrastructure & Cloud Deployment (IaC)

## 1. Objective & Context
*   **Goal**: Define the production infrastructure as code for scalable, secure deployment on AWS/GCP.
*   **Rationale**: Ensures consistent environments, automated scaling, and reliable disaster recovery for the SaaS platform.
*   **Files Affected**:
    *   `Dockerfile`: Optimized multi-stage production build.
    *   `infra/terraform/`: AWS/GCP resource definitions.
    *   `.github/workflows/deploy.yml`: CD pipeline for automated infrastructure updates.

## 2. Research & Strategy
*   **Cloud**: AWS (ECS Fargate/RDS) or GCP (Cloud Run/Cloud SQL).
*   **Security**: Private subnets, VPC peering, and encrypted data volumes.
*   **IaC**: Terraform for resource provisioning; Helm (if using K8s).

## 3. Implementation Checklist
- [ ] **Production Dockerfile**: Build a slim, secure image with non-root user execution.
- [ ] **VPC & Networking**: Define public/private subnets and load balancer configuration.
- [ ] **Database Provisioning**: Setup RDS/Cloud SQL with automated backups and encryption.
- [ ] **App Service**: Configure ECS Fargate or Cloud Run with autoscaling rules based on CPU/Memory.
- [ ] **Secrets Management**: Integrate AWS Secrets Manager or GCP Secret Manager for API keys and DB credentials.
- [ ] **Monitoring**: Setup CloudWatch/Stackdriver dashboards and alerting for service health.

## 4. Testing & Verification (Mandatory)
### 4.1 Infrastructure Testing
- [ ] `terraform plan`: Verify resource changes before application.
- [ ] `checkov`: Run static analysis on Terraform files for security best practices.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: Automated Failover (Service remains available if one availability zone goes down).
- [ ] **Scenario**: Scaling Policy (System adds instances during high-traffic load).
- [ ] **Scenario**: Clean Tear-down (Verify all resources are correctly destroyed without leaving orphan costs).

## 5. Demo & Documentation
- [ ] **Architecture Diagram**: Provide a visual representation of the cloud infrastructure.
- [ ] **Deployment Guide**: Internal documentation for the DevOps team.

## 6. Engineering Standards
*   **Least Privilege**: IAM roles must have the minimum permissions required to operate.
*   **Immutable Infra**: Never make manual changes to production resources; always use Terraform.
*   **Cost Management**: Tag all resources for cost tracking and implement budget alerts.
