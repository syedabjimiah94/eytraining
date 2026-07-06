Playbook 1 — Running Self-Healing Weather System (Local & Docker)

--------------------------------------------------------------------------------------------
Purpose: Run the full Self-Healing Weather System stack for development or evaluation.
Audience: Developers / Reviewers / Evaluators.
Time: ~10–15 minutes (first build may take longer).

--------------------------------------------------------------------------------------------

1. Prerequisites
• Python 3.11+
• Docker Desktop (optional but recommended)
• Git installed
• .env file with required API keys (if applicable)

--------------------------------------------------------------------------------------------

2. Option A — Run Locally with Python (Development Mode)
Step 1: Clone the repository
git clone <repo-url>
cd self-healing-weather-system


Step 2: Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Linux/Mac


Step 3: Install dependencies
pip install -r requirements.txt


Step 4: Setup environment variables
cp .env.example .env
# Edit .env and add required API keys


Step 5: Start the system
python start.py
3. Expected Output
• Backend services start successfully
• Agents initialize (Monitor, Diagnosis, Healing, Validator)
• Logs appear in backend/app/logs/app.log


4. Health Check
curl http://localhost:8000/health


5. Stop System
CTRL + C

--------------------------------------------------------------------------------------------