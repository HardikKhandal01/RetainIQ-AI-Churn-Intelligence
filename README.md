# 🚀 RetainIQ — AI Churn Intelligence & Automated Retention SaaS

RetainIQ is a production-grade, end-to-end Machine Learning SaaS platform designed to predict customer churn, segment users dynamically based on behavioral metrics, and trigger real-time automated retention workflows.

---

## 🛠️ Tech Stack & Architecture
* **Frontend:** React, TypeScript, Vite, Tailwind CSS, Lucide Icons, Recharts.
* **Backend:** FastAPI, Python, SQLAlchemy ORM, SQLite / PostgreSQL.
* **Machine Learning:** Scikit-Learn, Joblib (Custom Preprocessor Pipelines & Logistic Regression / KMeans Models).
* **Automation:** n8n Webhook Triggers for instant high-risk customer alerting.

---

## 📂 Project Structure

retainiq/
├── backend/               # FastAPI Backend & ML Service
│   ├── app/
│   │   ├── core/          # Database connection
│   │   ├── models/        # SQLAlchemy Database models
│   │   ├── services/      # ML inference logic & bulk processing
│   │   └── main.py        # API Endpoints & Webhook triggers
├── frontend/              # React + Vite + Tailwind Dashboard
│   ├── src/               # UI Components & Dashboard views
├── ml/                    # Data Science Pipeline & Trained Artifacts
│   ├── artifacts/         # Joblib models & preprocessors
└── tests/                 # Pytest automated test suites

---

## ✨ Key Features
1. **Single Customer Prediction:** Real-time probability scoring, risk classification (Low, Medium, High, Critical), and detailed AI action plans with internal scrolling.
2. **Bulk CSV Upload & Pagination:** Upload large customer datasets (10,000+ rows) with instant KPI summary metrics (Total Revenue at Risk, High-Risk counts) and Gmail-style pagination.
3. **Interactive Sync:** Click any row in the bulk table to auto-populate the single prediction form for deep-dive analysis.
4. **Automated Workflows:** Background task webhooks designed to fire alerts to n8n when critical risk customers are identified.
5.