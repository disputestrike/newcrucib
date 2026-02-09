# CrucibAI Platform - Product Requirements Document

## Project Overview
**Name:** CrucibAI  
**Type:** Multi-Model AI Development Platform  
**Created:** February 9, 2026  
**Updated:** February 9, 2026  
**Status:** MVP Complete with Real AI Integration

---

## Original Problem Statement
Build CrucibAI - a complete AI development platform with:
- Multi-model AI integration (GPT-4o, Claude, Gemini)
- Working AI chat on landing page (no login required)
- 20 specialized AI agents for app generation
- Token-based pricing system
- RAG & hybrid search capabilities
- Document processing and analysis

---

## User Personas

### 1. Individual Developer
- Quick code questions and AI assistance
- Building personal projects and MVPs
- Uses free tier chat, upgrades for projects

### 2. Agency/Freelancer
- Multiple client projects per month
- Needs professional exports and documentation
- Uses Pro/Professional tier

### 3. Enterprise
- Large-scale application generation
- Custom model selection
- Uses Enterprise/Unlimited tier

---

## Core Features Implemented

### ✅ Multi-Model AI Chat
- **Real AI integration** using Emergent LLM Key
- Auto-selects best model based on task:
  - Code → Claude Sonnet
  - Analysis → GPT-4o
  - General → GPT-4o
  - Fast → Gemini 2.5 Flash
- Works on landing page without login
- Session persistence and history

### ✅ Landing Page Features
- Interactive AI chat box (works immediately)
- Hero section with CrucibAI branding
- 6 feature cards (Multi-Model AI, RAG, etc.)
- 4-layer agent visualization
- 4 pricing tiers
- Responsive design

### ✅ Authentication System
- Email/password registration
- Email/password login  
- JWT session management
- 50K free tokens on signup

### ✅ Token System
- 5 pricing tiers ($9.99-$999.99)
- Purchase flow (simulated)
- Transaction history
- Usage analytics by agent

### ✅ AI APIs
- `/api/ai/chat` - Multi-model chat with auto-selection
- `/api/ai/analyze` - Document analysis
- `/api/rag/query` - RAG-style queries
- `/api/search` - Hybrid search

### ✅ Project Generation
- 3-step wizard
- 20 agent orchestration (simulated)
- Real-time progress tracking
- Activity logging

### ✅ Dashboard
- Token balance display
- Weekly usage charts
- Recent projects
- Quick actions

---

## Technical Architecture

```
Frontend (React + Tailwind)
├── Landing Page (with AI Chat)
├── Auth (Login/Register)
└── App (Protected)
    ├── Dashboard
    ├── Project Builder
    ├── Agent Monitor
    ├── Token Center
    ├── Exports
    ├── Patterns
    └── Settings

Backend (FastAPI + MongoDB)
├── /api/ai/* (REAL AI - Emergent LLM)
│   ├── chat (multi-model)
│   ├── analyze (document processing)
├── /api/rag/* (RAG queries)
├── /api/search (hybrid search)
├── /api/auth/* (JWT auth)
├── /api/tokens/* (billing)
├── /api/projects/* (CRUD)
├── /api/agents/* (orchestration)
└── /api/patterns/* (library)
```

---

## What's REAL vs SIMULATED

### ✅ REAL (Working AI)
- AI Chat (GPT-4o, Claude, Gemini)
- Document Analysis
- RAG Queries
- Search
- User Authentication
- Token Tracking

### ⚠️ SIMULATED
- Token purchases (no Stripe)
- Agent orchestration (progress simulation)
- Export downloads (placeholder links)
- Deployment URLs (mock)

---

## Prioritized Backlog

### P0 - Critical
- [ ] Stripe payment integration
- [ ] Actual code generation with agents
- [ ] Real deployment to Vercel/Railway

### P1 - Important
- [ ] WebSocket for real-time updates
- [ ] Project code download
- [ ] Email notifications
- [ ] Team support

### P2 - Nice to Have
- [ ] Custom pattern creation
- [ ] Project templates
- [ ] API access for developers

---

## Success Metrics

### MVP Launch (Complete)
- [x] Real AI chat without login
- [x] Multi-model auto-selection
- [x] User registration/login
- [x] Token system
- [x] Project creation

### Next Milestone
- [ ] First paid customer (Stripe)
- [ ] 100 active users
- [ ] First real generated project

---

*Last Updated: February 9, 2026*
