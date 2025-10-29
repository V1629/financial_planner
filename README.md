# 💰 Smart Financial Planner
**An intelligent financial planner with AI-powered insights and trip planning.**

---

## 🧠 Overview
**Smart Financial Planner** is a full-stack Django web application that helps users **track expenses, visualize financial data, and receive AI-driven insights** through an integrated **RAG-based chatbot**.  

The system combines **traditional financial analytics** with **modern AI capabilities** (LangChain + Groq + Chroma + DuckDuckGo Search) to make budgeting and trip planning smarter.

---

## 🚀 Features

### 🧾 1. Financial Tracker & Analytics
- Add, view, and delete transactions  
- Track spending by category  
- Visualize spending with charts (pie, box, violin plots)  
- Smart insights (average, max, min, std deviation, top category, etc.)  

### 🤖 2. AI RAG Chatbot
- Connected with **Groq LLM (Mixtral 8x7B)**  
- Stores transaction history in **Chroma vector database**  
- Uses **LangChain retrieval chain** for context-aware responses  
- Uses **DuckDuckGo Search** for trip planning or live travel data  
- Secure API key management via `.env`  

---

## 🏗️ Architecture Overview

```text
financial_planner/
│
├── accounts/                     # Main app for finance + AI features
│   ├── data_analysis.py          # Financial analytics and visualization
│   ├── rag_pipeline.py           # RAG chatbot logic using LangChain + Groq
│   ├── templates/                # HTML templates
│   │   ├── planner.html          # Main dashboard (budget tracker)
│   │   ├── analytics.html        # Visualization and insights
│   │   ├── chatbot.html          # AI RAG chatbot interface
│   ├── static/                   # Custom CSS/JS for UI
│   ├── data/
│   │   └── transactions.csv      # Sample or user transaction data
│   ├── .env                      # Contains GROQ_API_KEY (ignored by Git)
│   ├── views.py                  # Handles routes for analytics and chatbot
│   ├── models.py, forms.py       # Django ORM and form handling
│
├── financial_planner/            # Django project configuration
│   ├── settings.py               # Core settings
│   ├── urls.py                   # URL routing
│   ├── asgi.py / wsgi.py         # Entry points
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md

| Layer             | Technologies                                         |
| ----------------- | ---------------------------------------------------- |
| **Backend**       | Django, Python                                       |
| **AI/ML**         | LangChain 1.x, Groq LLM, ChromaDB, DuckDuckGo Search |
| **Frontend**      | HTML5, CSS3, Bootstrap 5                             |
| **Da| Layer       | Technologies                                         |
| ----------------- | ---------------------------------------------------- |
| **Backend**       | Django, Python                                       |
| **AI/ML**         | LangChain 1.x, Groq LLM, ChromaDB, DuckDuckGo Search |
| **Frontend**      | HTML5, CSS3, Bootstrap 5                             |
| **Database**      | SQLite (Django ORM)                                  |
| **Visualization** | Matplotlib, Pandas                                   |
| **Environment**   | `.env` for API keys, Python virtual environment      |
|**database**       | SQLite (Django ORM)                                  |
| **Visualization** | Matplotlib, Pandas                                   |
| **Environment**   | `.env` for API keys, Python virtual environment      |
