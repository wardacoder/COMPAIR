# COMPAIR  
**Intelligent decision-making through structured AI comparisons**

A full-stack web application that transforms decision paralysis into clarity. Built with React.js and FastAPI, and fully containerized with Docker, COMPAIR uses GPT-4o, LangChain, Brave Search, and structured JSON validation to deliver grounded, personalized comparisons across any category, including gadgets, cars, technologies, destinations, and more.

---

## 🎯 The Problem

Choosing between multiple options usually means:

- Sifting through scattered reviews  
- Opening too many tabs  
- Manually comparing specifications  
- Struggling to weigh trade-offs  

**COMPAIR solves this** by generating structured, validated, context-aware comparisons that adapt to your needs, priorities, and budget.

---

## ✨ Core Features

### 🤖 Intelligent Comparison Engine  
- Uses OpenAI GPT-4o through LangChain for structured AI reasoning  
- Generates comparison tables, pros and cons, summaries, and recommendations  
- Understands category context such as Gadgets, Cars, Technologies, Destinations, Shows, and more  
- Validates items with category-specific rules to prevent incorrect comparisons  
- Produces consistent structured JSON outputs through Pydantic parsing  

### 👤 Personalization  
- Users can provide priorities, a budget range, and a detailed use case  
- COMPAIR produces a personalized winner based on user needs  
- When preferences are not provided, COMPAIR provides neutral and balanced comparisons  

### 🔍 Real-Time Search Integration  
- Integrates Brave Search API to fetch real and current data for each item  
- Reduces hallucinations by grounding the model using factual search snippets  
- Search snippets are injected into prompts before LLM processing for accuracy  

### 💬 Context-Aware Follow-Up  
- Users can ask follow-up questions after receiving results  
- COMPAIR maintains conversation memory for each comparison  
- Follow-up answers stay relevant without restarting any session  

### 📚 History and Sharing  
- Stores comparisons in PostgreSQL using JSONB  
- Allows users to revisit, manage, and organize past comparisons  
- Generates public shareable links for quick access and collaboration  

### 📊 Insights and Analytics  
- Tracks popular items across categories  
- Highlights trending comparison categories  
- Provides high-level usage patterns  

### 🎨 Modern User Experience  
- Built with React 18 and TailwindCSS  
- Smooth interactions using Framer Motion  
- Fully responsive design  
- Clean and intuitive form controls, tabs, and results display  
- Light and dark mode support  
- Optional PDF exporting capability  

---

## 🛠️ Technical Architecture

COMPAIR is designed as a modular, scalable, and grounded full-stack system that connects frontend interaction, backend logic, AI reasoning, real-time search, and persistent data storage.

### Frontend  
- React.js 18  
- TailwindCSS  
- Framer Motion  
- Component-based structure  
- Fetch API for backend communication  
- Local storage for theme persistence  

### Backend  
- FastAPI with async support  
- Category validation and prompt construction  
- Brave Search integration  
- LangChain for GPT-4o orchestration and output parsing  
- Conversation memory for follow-up interactions  
- Comprehensive error handling and logging  

### AI Reasoning Layer  
- GPT-4o for structured and grounded comparisons  
- Real-time data from Brave Search  
- Dynamic prompt construction using system and user messages  
- Strict schema enforcement with PydanticOutputParser  

---
## 🎥 Project Demo

<p align="center">
  <a href="https://youtu.be/z6a9f1jB2SI" target="_blank">
    <img src="https://img.youtube.com/vi/z6a9f1jB2SI/0.jpg" alt="COMPAIR Demo" width="700">
  </a>
</p>

<p align="center">
  ▶ <a href="https://youtu.be/z6a9f1jB2SI" target="_blank"><b>Click here to watch the full COMPAIR demo on YouTube</b></a>
</p>

Static screenshots are available in  
📂 `COMPAIR/images`

---

## 🗄️ Database Overview

COMPAIR uses **PostgreSQL with JSONB** for fast and flexible structured storage.

Supports:

- Comparison history  
- Public shareable comparisons  
- Conversation memory  
- A 24-hour caching layer for reducing repeated LLM calls  
- Item analytics and frequency tracking  

### Why JSONB  
- Faster than plain JSON  
- Ideal for storing AI-generated tables, pros and cons, and structured results  
- Works seamlessly with PostgreSQL indexing and filtering  

---

## 📂 Repository Structure

```
COMPAIR/
├── backend/
│   ├── main.py
│   ├── prompt/
│   ├── models/
│   ├── utilities/
│   └── database/
│
├── frontend/
│   ├── public/
│   ├── src/
│   └── package.json
│
├── Dockerfile
├── docker-compose.yml
├── .env (ignored)
├── images/
└── README.md
```

---

## 🐳 Docker Deployment (Short and Simple)

COMPAIR includes a complete, ready-to-run Docker setup.

### Containers  
- Backend (FastAPI with GPT-4o integration)  
- Frontend (React served with Nginx)  
- PostgreSQL (JSONB optimized)  

### Quick Start  
```bash
docker-compose up --build
```

### Access  
- Frontend: http://localhost:3000  
- Backend API: http://localhost:8000  
- Documentation: http://localhost:8000/docs  

---

## 🧪 Testing Overview

### Backend  
- Endpoint stability  
- Prompt construction logic  
- Brave Search integration  
- Schema validation  
- Error handling  

### AI Layer  
- Structured responses  
- Category consistency  
- Correct personalization  
- Hallucination reduction  

### Frontend  
- Form validation  
- Responsive UI  
- Flow stability  
- Animation performance  

### Integration  
- Context retention  
- End-to-end API reliability  
- History and sharing workflows  

---

## 🧠 Learning Outcomes

Developing **COMPAIR** strengthened my full-stack and AI engineering capabilities across all layers of system design.  
This project evolved from a simple comparison tool into a grounded, database-backed, cache-aware, multi-service AI system.

### Full-Stack Architecture  
Designed and delivered a complete React and FastAPI system with clean API contracts and structured data flows between frontend, backend, AI reasoning, and storage layers.

### Backend Engineering  
Built a production-ready backend with Brave Search grounding, a 24-hour caching layer, dynamic prompt templates, conversation memory, category filtering, and the repository pattern for clean data access.

### AI Integration and Prompt Engineering  
Developed a reliable prompt-engineering workflow using GPT-4o, LangChain, PydanticOutputParser, system and human messages, real-time grounding, anti-hallucination strategies, and dynamic prompt construction.

### Database Design and Data Engineering  
Implemented PostgreSQL with JSONB storage, optimized indexing, TTL caches, history management, public sharing, item analytics, and stable data flows.

### Frontend Development  
Built a modern, responsive UI with React, TailwindCSS, Framer Motion, and clean state management patterns to present structured AI outputs effectively.

### DevOps and Deployment  
Containerized all services with Docker, configured Nginx for production frontend hosting, and set up environment-based configuration for portability.

### System Thinking  
Learned how to combine human preferences, AI reasoning, real-time grounding, backend orchestration, structured validation, and clean UI into one cohesive product.

---

## ✨ Author

**Warda Ul Hasan**  
Computer Engineering Graduate, American University of Sharjah  
LinkedIn: https://www.linkedin.com/in/wardaulhasan  
GitHub: https://github.com/wardacoder  

> COMPAIR reflects my goal to build systems where intelligence meets structure, practical purpose, and thoughtful design.
