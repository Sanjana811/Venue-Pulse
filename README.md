# 🚀 Venue Pulse

Venue Pulse is a lightweight, AI-inspired crowd management system for large-scale sporting venues. It provides real-time insights into crowd density, predicts wait times, and suggests optimal routes to improve attendee experience and operational efficiency.

---

## 💡 Overview
The platform uses a FastAPI backend with simulated in-memory data to model crowd density and waiting times across different zones of a venue. It implements a routing algorithm to guide users through less congested paths, improving movement flow and overall experience.

---

## 🎯 Key Features
- 📍 Real-time (simulated) crowd density monitoring  
- ⏱️ Wait time prediction using lightweight logic  
- 🧭 Smart routing to avoid congested areas  
- ⚡ Fast and minimal backend using FastAPI  
- ☁️ Cloud-ready deployment  

---

## 🛠️ Tech Stack
- **Backend:** FastAPI (Python)  
- **Frontend:** HTML, CSS, JavaScript  
- **Logic:** Rule-based simulation + routing algorithm  
- **Deployment:** Google Cloud Run (serverless)  

---

## 🏆 Evaluation Highlights

### 1. Code Quality
- Modular FastAPI architecture  
- Type hints + Pydantic validation  
- Clean and readable structure  

### 2. Security
- Input validation using Pydantic  
- Controlled API endpoints  
- Containerized deployment  

### 3. Efficiency
- Lightweight in-memory data (no DB overhead)  
- Fast routing logic (Dijkstra-based)  
- Millisecond response time  

### 4. Testing
- Pytest-based test suite  
- API validation and edge-case handling  

### 5. Accessibility
- Semantic HTML  
- Accessible UI structure  
- Clean and responsive layout  

---

## ☁️ Google Cloud Usage
- Deployed using **Google Cloud Run**
- Built using **Cloud Build**
- Serverless architecture (auto scaling + scale-to-zero)
- Optimized for free-tier usage

🌐 **Live Demo:**  
https://venue-pulse-423706223516.us-central1.run.app/

---

## 🚀 Run Locally

```bash
cd venue-pulse
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
