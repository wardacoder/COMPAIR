# COMPAIR  
**Intelligent decision-making through structured AI comparisons**

A full-stack web application that transforms decision paralysis into clarity. Built with React.js and FastAPI, and fully containerized with Docker, COMPAIR uses GPT-4o, LangChain, Brave Search, structured JSON validation, and an MCP (Model Context Protocol) layer to deliver grounded, personalized comparisons across any category, including gadgets, cars, technologies, destinations, and more.

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

### 📊 Analytics Dashboard  
- Dedicated dashboard page with time-range filtering (7, 30, 90 days)  
- Displays total comparisons, category breakdowns, popular comparison pairs, and decision confidence metrics  
- Tracks user feedback statistics including ratings and improvement comments  
- Integrated AI chat lets users ask natural-language questions about their comparison history  

### ⭐ User Feedback System  
- Collects star ratings for accuracy and winner match quality after each comparison  
- Separate feedback paths for personalized and neutral comparisons  
- Stores user comments (what worked, what could improve) in PostgreSQL for analytics  

### 🔌 MCP (Model Context Protocol) Layer  
- A dedicated FastAPI MCP server runs alongside the main backend (port 8001)  
- Exposes 9 structured tools covering dashboard metrics, feedback summaries, category insights, activity trends, and AI-generated reports  
- Any MCP-compatible AI assistant (Grok, ChatGPT, Claude) can connect and query COMPAIR data programmatically  
- `mcp_config.json` provided for easy AI assistant configuration  

### 📚 Comparison History and Sharing  
- Stores all comparisons in PostgreSQL using JSONB  
- Generates public shareable links for quick access and collaboration  

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
- MCP server (separate FastAPI service on port 8001) exposing dashboard data as AI-callable tools  
- Comprehensive error handling and logging  

### AI Reasoning Layer  
- GPT-4o for structured and grounded comparisons  
- Groq LLM for analytics chat responses via the MCP layer  
- Real-time data from Brave Search  
- Dynamic prompt construction using system and human messages  
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
│   ├── main.py                    # Core API (port 8000)
│   ├── mcp_server.py              # MCP server — AI tool layer (port 8001)
│   ├── grok_mcp_client.py         # MCP client for AI assistant integration
│   ├── analytics_chat_endpoint.py # Analytics chat API endpoint
│   ├── prompt/
│   ├── models/
│   ├── utilities/
│   └── database/
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/            # Includes AnalyticsChat, FeedbackSection
│   │   └── pages/                 # Compare, Dashboard, Home
│   └── package.json
│
├── docs/                          # Technical deep-dives and implementation notes
├── docker-compose.yml             # 4-service orchestration
├── mcp_config.json                # AI assistant MCP configuration
├── .env.example                   # Environment template
├── images/
└── README.md
```

---

## 🐳 Docker Deployment

COMPAIR includes a complete, ready-to-run Docker setup.

### Containers  
- Backend (FastAPI with GPT-4o integration) — port 8000  
- MCP Server (AI tool layer) — port 8001  
- Frontend (React served with Nginx) — port 3000  
- PostgreSQL (JSONB optimized)  

### Quick Start  
```bash
cp .env.example .env   # fill in your API keys
docker-compose up --build
```

### Access  
- Frontend: http://localhost:3000  
- Backend API: http://localhost:8000  
- MCP Server: http://localhost:8001  
- API Documentation: http://localhost:8000/docs  

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
Built a production-ready backend with Brave Search grounding, a 24-hour PostgreSQL-backed caching layer, dynamic prompt templates, conversation memory, category filtering, a dedicated MCP server exposing structured AI tools, and the repository pattern for clean data access.

### AI Integration and Prompt Engineering  
Developed a reliable prompt-engineering workflow using GPT-4o, LangChain, PydanticOutputParser, system and human messages, real-time grounding, anti-hallucination strategies, and dynamic prompt construction. Extended the AI layer with Groq for analytics chat and MCP tool-calling for structured data queries.

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


