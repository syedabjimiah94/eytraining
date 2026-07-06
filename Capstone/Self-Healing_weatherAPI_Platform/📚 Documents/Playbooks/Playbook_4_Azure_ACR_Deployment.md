Playbook 4 — Azure ACR Deployment for Self-Healing Weather System

--------------------------------------------------------------------------------------------
Purpose: Build, containerize, and deploy the Self-Healing Weather System Docker image to Azure Container Registry (ACR).
Audience: DevOps Engineers / Cloud Engineers.
Time: ~15–25 minutes.

--------------------------------------------------------------------------------------------
1. Prerequisites
• Azure Subscription
• Azure CLI installed (az)
• Docker installed
• Git repository cloned locally
• Azure Container Registry (ACR) created


2. Step 1 — Login to Azure
az login


3. Step 2 — Set Subscription (if multiple)
az account set --subscription <subscription-id>


4. Step 3 — Create Resource Group (if needed)
az group create -n selfheal-rg -l centralindia


5. Step 4 — Create Azure Container Registry
az acr create -n selfhealacr -g selfheal-rg --sku Basic


6. Step 5 — Login to ACR
az acr login --name selfhealacr


7. Step 6 — Build Docker Image
docker build -t selfheal-weather:latest .


8. Step 7 — Tag Image for ACR
docker tag selfheal-weather selfhealacr.azurecr.io/selfheal-weather:latest


9. Step 8 — Push Image to ACR
docker push selfhealacr.azurecr.io/selfheal-weather:latest


10. Step 9 — Verify Image in ACR
az acr repository list --name selfhealacr


11. Step 10 — Run Image from ACR (optional)
docker run -p 8000:8000 selfhealacr.azurecr.io/selfheal-weather:latest


12. Troubleshooting
• Ensure Docker daemon is running
• Ensure Azure login session is active
• Check ACR permissions (AcrPush role)
• Validate image tag format

--------------------------------------------------------------------------------------------