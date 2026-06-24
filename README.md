# cinemind-AI
AI-powered movie discovery platform (React + FastAPI + ML)
# CineMind AI — Intelligent Movie Discovery Platform

A full-stack, AI-powered movie discovery platform built to learn and demonstrate real-world full-stack + ML engineering.

## 🚧 Project Status
This project is being built incrementally and documented stage by stage.

- [x] Stage 0: Project setup
- [ ] Stage 1: Movie recommendation engine (Python + Pandas + TF-IDF)
- [ ] Stage 2: REST API (FastAPI)
- [ ] Stage 3: Frontend (React + Next.js + Tailwind)
- [ ] Stage 4: Auth, database, AI chatbot, analytics dashboard, deployment

## Features (planned)
- AI-powered movie recommendations (content-based, using TF-IDF + cosine similarity)
- Natural language movie search
- User accounts, watchlists, ratings & reviews
- AI movie assistant chatbot
- Trending analytics dashboard
- Cloud deployment

## Tech Stack
**Frontend:** React, Next.js, Tailwind CSS, Framer Motion, Chart.js
**Backend:** Python, FastAPI
**Database:** PostgreSQL (Neon)
**AI/ML:** Pandas, NumPy, Scikit-Learn, TF-IDF, Cosine Similarity
**Auth:** JWT
**Deployment:** Vercel (frontend), Render (backend), Neon (database)

## Project Structure
\`\`\`
cinemind-ai/
├── backend/
│   ├── app.py
│   ├── models/
│   ├── routes/
│   ├── recommendation/
│   ├── auth/
│   └── database/
├── frontend/
├── dataset/
└── docs/
\`\`\`

## Setup (Backend)
\`\`\`bash
cd backend
python3 -m venv venv
source venv/bin/activate   # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
\`\`\`

## Author
Built by Harsh Mishta — B.Tech IT student, learning full-stack + ML development.