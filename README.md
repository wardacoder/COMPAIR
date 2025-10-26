# COMPAIR 

**Intelligent decision-making through structured AI comparisons**

A full-stack web application that transforms decision paralysis into clarity. Built with React.js and FastAPI, COMPAIR uses LangChain and OpenAI's GPT-4o to deliver structured, personalized comparisons across any category from gadgets to destinations or anything that matters to you.

---

## 🎯 The Problem

Making informed choices between multiple options often means:
- Drowning in unstructured online reviews
- Spending hours comparing specifications manually
- Struggling to weigh priorities against available options

**COMPAIR solves this** by providing AI-generated, structured comparisons that adapt to your specific needs, budget, and use case.

---

## ✨ Core Features

### 🤖 Intelligent Comparison Engine
- **Category-aware AI** that understands context (gadgets, cars, technologies, destinations, shows)
- **Structured outputs**: comparison tables, pros/cons analysis, and evidence-based recommendations
- **Smart validation**: prevents nonsensical comparisons through category-specific grounding

### 👤 Personalization
- Define your **priorities** (e.g., "battery life, camera quality")
- Set your **budget** constraints
- Describe your **use case** (e.g., "professional photography vs casual use")
- Receive a **personalized winner** recommendation tailored to your needs

### 💬 Context-Aware Follow-Up
- Ask clarifying questions after receiving results
- AI maintains conversation context for coherent, relevant answers
- Explore deeper comparisons without starting over

### 🎨 User Experience
- **Responsive design** with dark/light mode support
- **Smooth animations** powered by Framer Motion
- **Persistent history**: save, share, and revisit past comparisons
- **Export capabilities**: PDF generation for offline reference

---

## 🛠️ Technical Architecture

### Tech Stack

| Layer | Technologies |
|-------|---------------|
| **Frontend** | React.js, TailwindCSS, Framer Motion |
| **Backend** | FastAPI, Python, Pydantic, Uvicorn |
| **AI Layer** | LangChain, OpenAI API (GPT-4o) |
| **Dev Tools** | dotenv, Git, Node.js |

### System Flow

```
┌─────────────────┐
│  React Frontend │
│   (User Input)  │
└────────┬────────┘
         │ REST API
         ▼
┌─────────────────┐
│  FastAPI Server │
│  - Validation   │
│  - Prompt Build │
└────────┬────────┘
         │ LangChain
         ▼
┌─────────────────┐
│  OpenAI GPT-4o  │
│  (AI Reasoning) │
└────────┬────────┘
         │ Structured JSON
         ▼
┌─────────────────┐
│ Pydantic Parser │
│   (Validation)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  React UI       │
│  (Results View) │
└─────────────────┘
```

**Data Flow:**
1. User submits items, category, and optional preferences
2. Backend validates input and constructs category-specific prompts
3. LangChain orchestrates OpenAI API call with structured output requirements
4. Pydantic validates response schema and ensures data integrity
5. Frontend renders structured comparison with interactive elements
6. Follow-up questions maintain context through conversation state

---
## 📂 Repository Structure

```
COMPAIR/
├── .gitignore                     # Ensures unwanted files (node_modules, .env, cache) aren’t committed
│
├── backend/
│   ├── main.py                    # FastAPI backend – AI logic, endpoints, and validation
│   ├── requirements.txt           # Python dependencies
│   └── .env.example               # Template for environment variables (OPENAI_API_KEY)
│
├── frontend/
│   ├── package.json               # Frontend dependencies and scripts
│   ├── package-lock.json          # Dependency lock file
│   ├── public/                    # Static assets (index.html uses Tailwind via CDN)
│   │   └── index.html
│   └── src/                       # React source code
│       ├── App.js
│       ├── index.js
│       ├── components/            # Reusable UI components (forms, tabs, chat, etc.)
│       └── pages/                 # Main app views (Home, Compare, History)
│
├── images/                        # Screenshots displayed in README
│
├── README.md                      # Project documentation (this file)
└── LICENSE                        # License information 
```
---
## 🎥 Project Demo

<p align="center">
  <a href="https://youtu.be/200wY4brWrg" target="_blank">
    <img src="https://img.youtube.com/vi/200wY4brWrg/0.jpg" alt="COMPAIR Demo" width="700">
  </a>
</p>

<p align="center">
  ▶ <a href="https://youtu.be/z6a9f1jB2SI" target="_blank"><b>Click here to watch the full COMPAIR demo on YouTube</b></a>
</p>

---

If you prefer to view static visuals instead, all screenshots are available in the repository at:  
📂 [`COMPAIR/images`](./images)

---

## 🧱 Backend Architecture

The backend of **COMPAIR** is built using **FastAPI**, designed for scalability, modularity, and efficient AI integration.  
It serves as the system’s logic core — managing input validation, AI orchestration, and data persistence.

Key endpoints include `/compare`, `/ask-followup`, `/save-comparison`, `/share-comparison`, and `/history`.  
Each request undergoes schema validation, category filtering, and dynamic prompt construction.  
AI responses are processed through LangChain’s pipeline, parsed with Pydantic, and then returned as structured, human-readable JSON.

The backend architecture emphasizes:
- Clean separation of logic  
- Robust error handling with FastAPI’s exception management  
- Logging and traceability for every AI interaction  
- Schema validation for predictable outputs

### 🧠 AI Integration and Prompt Design

The intelligence behind **COMPAIR** is powered through **prompt engineering**, **grounding techniques**, and **structured output control** implemented with **LangChain** and the **OpenAI API**.  
The backend uses carefully designed system and user prompts to ensure that the model generates **consistent**, **category-relevant**, and **validated JSON outputs** for every comparison request.

#### 🧩 Category-Specific Prompting
COMPAIR dynamically adjusts its comparison logic based on the selected **category**, such as *Gadgets*, *Cars*, *Technologies*, *Destinations*, *Shows*, or *Other*.  
Each category defines its own semantic boundaries and validation rules to ensure the AI only compares contextually relevant items.  

If items don’t belong to the chosen category or are nonsensical (e.g., “a” vs “b”), the AI returns a validation message rather than an invalid comparison.  
This category-grounded prompting ensures the model remains context-aware and produces only meaningful outputs.

#### 🧭 Personalized Recommendations
User preferences — such as **budget**, **priorities**, and **use case** — are dynamically inserted into the prompt before model invocation if the user wants. The user may leave out this option where the results will only show a comparison without an indication of which suits the user better.
Depending on whether preferences are provided, COMPAIR modifies the system instructions in real time to either include a **personalized winner** or offer a balanced **recommendation**.

#### ⚙️ Grounding and Output Validation
All AI responses are parsed using **LangChain’s PydanticOutputParser**, which enforces schema integrity and prevents malformed outputs.  
This validation layer guarantees that only structured, contextually grounded data is rendered in the frontend.

Together, these prompt-engineering strategies transform the model from a generic text generator into a **reliable, domain-aware decision-support system**.

---

## 💻 Frontend Architecture

The frontend of **COMPAIR** is developed with **React.js**, featuring a modular, component-based structure that ensures clarity, scalability, and responsiveness. The interface delivers a seamless experience that connects all stages of interaction — from item input to personalized AI-driven results.

It comprises four core views:  
- **Home Page:** A clean, visually balanced landing screen that introduces COMPAIR and its AI-assisted comparison concept.  
- **Comparison Interface:** Users can select categories, enter items, and personalize preferences such as priorities, budget, and use case. State hooks and modular components manage form logic and validation efficiently.  
- **Dynamic Results View:** Displays structured outputs — comparison tables, pros and cons, and personalized recommendations — using conditional rendering for clarity.  
- **Follow-Up Interaction:** Enables context-aware Q&A through a controlled chat interface that retains conversation history.

The frontend employs **TailwindCSS** for a consistent, responsive design system and **Framer Motion** for subtle animations that enhance feedback and interactivity. Together, these technologies create an intuitive, visually refined, and technically cohesive user experience.

---

### Testing Approach

**Backend Testing**
- ✅ API endpoint stability and error handling
- ✅ Schema validation across all response types
- ✅ Prompt construction logic for edge cases
- ✅ Category filtering and validation rules

**AI Output Validation**
- ✅ PydanticOutputParser enforcement
- ✅ Category-appropriate comparison verification
- ✅ Personalization logic correctness
- ✅ Hallucination prevention checks

**Frontend Testing**
- ✅ Form validation and user input handling
- ✅ Responsive design across devices
- ✅ State management for multi-step flows
- ✅ Animation performance and accessibility

**Integration Testing**
- ✅ End-to-end API communication
- ✅ Context retention in follow-up chat
- ✅ Error propagation and user feedback
- ✅ Cross-browser compatibility

---

## 🚀 Next Development Steps

- Integrate a database for persistent user data.  
- Add authentication and personalized dashboards.  
- Deploy via AWS (backend) and Vercel (frontend).  
- Expand comparison categories and template logic.  

---

## 🧠 Learning Outcomes

Developing **COMPAIR** provided a comprehensive set of engineering skills: spanning backend logic, frontend development, and controlled AI system integration.  

### ⚙️ Full-Stack Architecture
Implemented a complete **React.js–FastAPI** architecture with clean RESTful communication and modular scalability.

### 🧱 Backend Engineering
Designed endpoints, prompt orchestration, and response validation using **PydanticOutputParser**.  
Implemented category filtering, personalized winner logic, and robust error handling.

### 💻 Frontend Development
Built a responsive, modular UI with **React.js**, **TailwindCSS**, and **Framer Motion**, connected to the backend through structured API calls.

### 🧠 AI Integration & Prompt Design
Developed **system** and **user messages** that define model behavior and context.  
System messages enforce JSON schema and category rules, while user messages dynamically add preferences and item data.  
Focused on eliminating hallucinations and ensuring structured, context-aware outputs.

### 🎨 Product Design
Converted structured AI outputs into readable, visual comparisons for better decision-making and clarity.

### 🧪 Testing & Integration
Validated all endpoints and outputs through functional, integration, and manual testing for stability and logical consistency.

### 🧭 System Thinking
Approached the project holistically — integrating human interaction, AI reasoning, and backend reliability into a unified system.

This project has given me a **comprehensive skill set** — from backend API design and validation to frontend UI/UX development and AI integration at the reasoning level.  
It strengthened my ability to design systems where each layer — human, software, and AI — communicates clearly, reliably, and purposefully.

---

## 🪪 License

© 2025 Warda Hasan. All rights reserved.

This project is intended for educational and portfolio demonstration purposes only.  
No part of this repository may be copied, modified, or distributed without explicit permission from the author.  
Recruiters and collaborators are welcome to explore the code for review and evaluation.

---

## ✨ Author

**Warda UL Hasan**  
🎓 Computer Engineering Graduate – American University of Sharjah  
💡 Interests: Full-Stack Engineering · AI Systems · Research & Innovation  
🔗 [LinkedIn](https://www.linkedin.com/in/wardaulhasan) | [GitHub](https://github.com/wardacoder)

> *COMPAIR reflects my commitment to designing systems where intelligence meets structure: practical, purposeful, and human-centered.*



