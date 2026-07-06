Playbook 3 — GitHub Actions CI/CD Pipeline for Self-Healing Weather System

--------------------------------------------------------------------------------------------
Purpose: Automate build, test, and deployment of the Self-Healing Weather System using GitHub Actions.
Audience: Developers / DevOps Engineers.
Trigger: Push to main branch or pull request.

1. Prerequisites
• GitHub repository
• Dockerfile in project root
• Azure Container Registry (ACR)
• GitHub Secrets configured


2. Required GitHub Secrets
• AZURE_CLIENT_ID
• AZURE_TENANT_ID
• AZURE_SUBSCRIPTION_ID
• ACR_LOGIN_SERVER
• ACR_USERNAME
• ACR_PASSWORD


3. Workflow File Location
.github/workflows/ci-cd.yml


4. Step 1 — Trigger Conditions
The pipeline triggers automatically on push or pull request to main branch.


5. Step 2 — Checkout Code
uses: actions/checkout@v3


6. Step 3 — Setup Docker Build
uses: docker/setup-buildx-action@v3


7. Step 4 — Login to ACR
uses: azure/docker-login@v1


8. Step 5 — Build Image
docker build -t ${{ secrets.ACR_LOGIN_SERVER }}/selfheal-weather:latest .


9. Step 6 — Push Image
docker push ${{ secrets.ACR_LOGIN_SERVER }}/selfheal-weather:latest


10. Step 7 — Run Tests (Optional)
pytest tests/


11. Step 8 — Deployment Verification
After successful push, the image is available in Azure Container Registry and can be deployed to Azure App Service or Kubernetes.


12. Rollback Strategy
If deployment fails, redeploy previous stable image tag from ACR.


13. Monitoring
GitHub Actions logs provide build status, push status, and deployment verification.

--------------------------------------------------------------------------------------------