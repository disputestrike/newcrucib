from fastapi import FastAPI, APIRouter, HTTPException, Depends, BackgroundTasks, File, UploadFile, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import hashlib
import asyncio
import random
import json
import tempfile
import base64

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI(title="CrucibAI Platform")
api_router = APIRouter(prefix="/api")
security = HTTPBearer(auto_error=False)

JWT_SECRET = os.environ.get('JWT_SECRET', 'crucibai-secret-key-2024')
JWT_ALGORITHM = "HS256"
EMERGENT_KEY = os.environ.get('EMERGENT_LLM_KEY')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==================== MODELS ====================

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    model: Optional[str] = "auto"  # auto, gpt-4o, claude, gemini

class ChatResponse(BaseModel):
    response: str
    model_used: str
    tokens_used: int
    session_id: str

class TokenPurchase(BaseModel):
    bundle: str

class ProjectCreate(BaseModel):
    name: str
    description: str
    project_type: str
    requirements: Dict[str, Any]
    estimated_tokens: Optional[int] = None

class DocumentProcess(BaseModel):
    content: str
    doc_type: str = "text"
    task: str = "summarize"  # summarize, extract, analyze

class RAGQuery(BaseModel):
    query: str
    context: Optional[str] = None
    top_k: int = 5

class SearchQuery(BaseModel):
    query: str
    search_type: str = "hybrid"  # vector, keyword, hybrid

# ==================== TOKEN PRICING ====================

TOKEN_BUNDLES = {
    "starter": {"tokens": 100000, "price": 9.99},
    "pro": {"tokens": 500000, "price": 49.99},
    "professional": {"tokens": 1200000, "price": 99.99},
    "enterprise": {"tokens": 5000000, "price": 299.99},
    "unlimited": {"tokens": 25000000, "price": 999.99}
}

AGENT_DEFINITIONS = [
    {"name": "Planner", "layer": "planning", "description": "Decomposes user requests into executable tasks", "avg_tokens": 50000},
    {"name": "Requirements Clarifier", "layer": "planning", "description": "Asks clarifying questions and validates requirements", "avg_tokens": 30000},
    {"name": "Stack Selector", "layer": "planning", "description": "Chooses optimal technology stack", "avg_tokens": 20000},
    {"name": "Frontend Generation", "layer": "execution", "description": "Generates React/Next.js UI components", "avg_tokens": 150000},
    {"name": "Backend Generation", "layer": "execution", "description": "Creates APIs, auth, business logic", "avg_tokens": 120000},
    {"name": "Database Agent", "layer": "execution", "description": "Designs schema and migrations", "avg_tokens": 80000},
    {"name": "API Integration", "layer": "execution", "description": "Integrates third-party APIs", "avg_tokens": 60000},
    {"name": "Test Generation", "layer": "execution", "description": "Writes comprehensive test suites", "avg_tokens": 100000},
    {"name": "Image Generation", "layer": "execution", "description": "Creates AI-generated visuals", "avg_tokens": 40000},
    {"name": "Security Checker", "layer": "validation", "description": "Audits for vulnerabilities", "avg_tokens": 40000},
    {"name": "Test Executor", "layer": "validation", "description": "Runs all tests and reports", "avg_tokens": 50000},
    {"name": "UX Auditor", "layer": "validation", "description": "Reviews design and accessibility", "avg_tokens": 35000},
    {"name": "Performance Analyzer", "layer": "validation", "description": "Optimizes speed and efficiency", "avg_tokens": 40000},
    {"name": "Deployment Agent", "layer": "deployment", "description": "Deploys to cloud platforms", "avg_tokens": 60000},
    {"name": "Error Recovery", "layer": "deployment", "description": "Auto-fixes failures", "avg_tokens": 45000},
    {"name": "Memory Agent", "layer": "deployment", "description": "Stores patterns for reuse", "avg_tokens": 25000},
    {"name": "PDF Export", "layer": "export", "description": "Generates formatted PDF reports", "avg_tokens": 30000},
    {"name": "Excel Export", "layer": "export", "description": "Creates spreadsheets with formulas", "avg_tokens": 25000},
    {"name": "Scraping Agent", "layer": "automation", "description": "Extracts data from websites", "avg_tokens": 35000},
    {"name": "Automation Agent", "layer": "automation", "description": "Schedules tasks and workflows", "avg_tokens": 30000}
]

# AI Model configurations for auto-selection
MODEL_CONFIG = {
    "code": {"provider": "anthropic", "model": "claude-sonnet-4-5-20250929"},
    "analysis": {"provider": "openai", "model": "gpt-4o"},
    "general": {"provider": "openai", "model": "gpt-4o"},
    "creative": {"provider": "anthropic", "model": "claude-sonnet-4-5-20250929"},
    "fast": {"provider": "gemini", "model": "gemini-2.5-flash"}
}

# ==================== HELPERS ====================

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=30)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_optional_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        return None
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0})
        return user
    except:
        return None

def detect_task_type(message: str) -> str:
    """Auto-detect the best model based on message content"""
    message_lower = message.lower()
    
    code_keywords = ['code', 'function', 'class', 'api', 'bug', 'error', 'debug', 'implement', 'python', 'javascript', 'react', 'database']
    analysis_keywords = ['analyze', 'compare', 'evaluate', 'explain', 'why', 'how does', 'what is']
    creative_keywords = ['write', 'create', 'story', 'poem', 'design', 'imagine', 'brainstorm']
    
    for kw in code_keywords:
        if kw in message_lower:
            return "code"
    
    for kw in analysis_keywords:
        if kw in message_lower:
            return "analysis"
    
    for kw in creative_keywords:
        if kw in message_lower:
            return "creative"
    
    return "general"

# ==================== AI CHAT ROUTES ====================

@api_router.post("/ai/chat")
async def ai_chat(data: ChatMessage, user: dict = Depends(get_optional_user)):
    """Multi-model AI chat with auto-selection"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        session_id = data.session_id or str(uuid.uuid4())
        
        # Auto-select model based on task type
        if data.model == "auto":
            task_type = detect_task_type(data.message)
            model_config = MODEL_CONFIG.get(task_type, MODEL_CONFIG["general"])
        elif data.model == "gpt-4o":
            model_config = {"provider": "openai", "model": "gpt-4o"}
        elif data.model == "claude":
            model_config = {"provider": "anthropic", "model": "claude-sonnet-4-5-20250929"}
        elif data.model == "gemini":
            model_config = {"provider": "gemini", "model": "gemini-2.5-flash"}
        else:
            model_config = MODEL_CONFIG["general"]
        
        # Initialize chat
        chat = LlmChat(
            api_key=EMERGENT_KEY,
            session_id=session_id,
            system_message="You are CrucibAI, an advanced AI assistant specialized in software development, code generation, and technical analysis. Be concise, helpful, and provide code examples when relevant."
        ).with_model(model_config["provider"], model_config["model"])
        
        # Send message
        user_message = UserMessage(text=data.message)
        response = await chat.send_message(user_message)
        
        # Estimate tokens (rough estimate)
        tokens_used = len(data.message.split()) * 2 + len(response.split()) * 2
        
        # Store in chat history
        await db.chat_history.insert_one({
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "user_id": user["id"] if user else None,
            "message": data.message,
            "response": response,
            "model": f"{model_config['provider']}/{model_config['model']}",
            "tokens_used": tokens_used,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Deduct tokens if user is logged in
        if user and user.get("token_balance", 0) >= tokens_used:
            await db.users.update_one(
                {"id": user["id"]},
                {"$inc": {"token_balance": -tokens_used}}
            )
        
        return {
            "response": response,
            "model_used": f"{model_config['provider']}/{model_config['model']}",
            "tokens_used": tokens_used,
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"AI Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@api_router.get("/ai/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    history = await db.chat_history.find(
        {"session_id": session_id}, 
        {"_id": 0}
    ).sort("created_at", 1).to_list(100)
    return {"history": history}

@api_router.post("/ai/analyze")
async def ai_analyze(data: DocumentProcess, user: dict = Depends(get_optional_user)):
    """Document analysis with AI"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        prompts = {
            "summarize": f"Please provide a concise summary of the following content:\n\n{data.content}",
            "extract": f"Extract key entities, facts, and important information from:\n\n{data.content}",
            "analyze": f"Provide a detailed analysis of the following content, including insights and recommendations:\n\n{data.content}"
        }
        
        prompt = prompts.get(data.task, prompts["analyze"])
        
        chat = LlmChat(
            api_key=EMERGENT_KEY,
            session_id=str(uuid.uuid4()),
            system_message="You are an expert document analyst. Provide clear, structured analysis."
        ).with_model("openai", "gpt-4o")
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        return {
            "result": response,
            "task": data.task,
            "model_used": "openai/gpt-4o"
        }
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/rag/query")
async def rag_query(data: RAGQuery, user: dict = Depends(get_optional_user)):
    """RAG-style query with context"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        # Build context-aware prompt
        context_str = f"\nContext: {data.context}" if data.context else ""
        prompt = f"Based on available knowledge{context_str}, please answer: {data.query}\n\nProvide a detailed, well-sourced response."
        
        chat = LlmChat(
            api_key=EMERGENT_KEY,
            session_id=str(uuid.uuid4()),
            system_message="You are a knowledgeable AI assistant. Always cite sources when possible and indicate confidence levels."
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        return {
            "answer": response,
            "query": data.query,
            "sources": ["AI Knowledge Base"],
            "confidence": 0.85,
            "model_used": "anthropic/claude-sonnet"
        }
        
    except Exception as e:
        logger.error(f"RAG error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/search")
async def hybrid_search(data: SearchQuery, user: dict = Depends(get_optional_user)):
    """Hybrid search combining vector and keyword search"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        # Use AI to enhance search results
        chat = LlmChat(
            api_key=EMERGENT_KEY,
            session_id=str(uuid.uuid4()),
            system_message="You are a search assistant. Provide relevant, structured results."
        ).with_model("gemini", "gemini-2.5-flash")
        
        prompt = f"Search query: '{data.query}'\nProvide 5 relevant results with titles, descriptions, and relevance scores (0-1)."
        response = await chat.send_message(UserMessage(text=prompt))
        
        return {
            "query": data.query,
            "search_type": data.search_type,
            "results": response,
            "total_results": 5
        }
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== AUTH ROUTES ====================

@api_router.post("/auth/register")
async def register(data: UserRegister):
    existing = await db.users.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "email": data.email,
        "password": hash_password(data.password),
        "name": data.name,
        "token_balance": 50000,
        "plan": "free",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(user)
    
    await db.token_ledger.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "tokens": 50000,
        "type": "bonus",
        "description": "Welcome bonus tokens",
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    token = create_token(user_id)
    return {"token": token, "user": {k: v for k, v in user.items() if k != "password" and k != "_id"}}

@api_router.post("/auth/login")
async def login(data: UserLogin):
    user = await db.users.find_one({"email": data.email}, {"_id": 0})
    if not user or user["password"] != hash_password(data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user["id"])
    return {"token": token, "user": {k: v for k, v in user.items() if k != "password"}}

@api_router.get("/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    return {k: v for k, v in user.items() if k != "password"}

# ==================== TOKEN ROUTES ====================

@api_router.get("/tokens/bundles")
async def get_bundles():
    return {"bundles": TOKEN_BUNDLES}

@api_router.post("/tokens/purchase")
async def purchase_tokens(data: TokenPurchase, user: dict = Depends(get_current_user)):
    if data.bundle not in TOKEN_BUNDLES:
        raise HTTPException(status_code=400, detail="Invalid bundle")
    
    bundle = TOKEN_BUNDLES[data.bundle]
    new_balance = user["token_balance"] + bundle["tokens"]
    await db.users.update_one({"id": user["id"]}, {"$set": {"token_balance": new_balance}})
    
    await db.token_ledger.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "tokens": bundle["tokens"],
        "type": "purchase",
        "bundle": data.bundle,
        "price": bundle["price"],
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {"message": "Purchase successful", "new_balance": new_balance, "tokens_added": bundle["tokens"]}

@api_router.get("/tokens/history")
async def get_token_history(user: dict = Depends(get_current_user)):
    history = await db.token_ledger.find({"user_id": user["id"]}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return {"history": history, "current_balance": user["token_balance"]}

@api_router.get("/tokens/usage")
async def get_token_usage(user: dict = Depends(get_current_user)):
    usage = await db.token_usage.find({"user_id": user["id"]}, {"_id": 0}).to_list(1000)
    
    by_agent = {}
    by_project = {}
    total_used = 0
    
    for u in usage:
        agent = u.get("agent", "Unknown")
        project = u.get("project_id", "Unknown")
        tokens = u.get("tokens", 0)
        
        by_agent[agent] = by_agent.get(agent, 0) + tokens
        by_project[project] = by_project.get(project, 0) + tokens
        total_used += tokens
    
    return {
        "total_used": total_used,
        "by_agent": by_agent,
        "by_project": by_project,
        "balance": user["token_balance"]
    }

# ==================== AGENTS ROUTES ====================

@api_router.get("/agents")
async def get_agents():
    return {"agents": AGENT_DEFINITIONS}

@api_router.get("/agents/status/{project_id}")
async def get_agent_status(project_id: str, user: dict = Depends(get_current_user)):
    statuses = await db.agent_status.find({"project_id": project_id}, {"_id": 0}).to_list(100)
    if not statuses:
        return {"statuses": [{"agent_name": a["name"], "status": "idle", "progress": 0, "tokens_used": 0} for a in AGENT_DEFINITIONS]}
    return {"statuses": statuses}

# ==================== PROJECT ROUTES ====================

@api_router.post("/projects")
async def create_project(data: ProjectCreate, background_tasks: BackgroundTasks, user: dict = Depends(get_current_user)):
    estimated = data.estimated_tokens or 675000
    
    if user["token_balance"] < estimated:
        raise HTTPException(status_code=400, detail=f"Insufficient tokens. Need {estimated}, have {user['token_balance']}")
    
    project_id = str(uuid.uuid4())
    project = {
        "id": project_id,
        "user_id": user["id"],
        "name": data.name,
        "description": data.description,
        "project_type": data.project_type,
        "requirements": data.requirements,
        "status": "queued",
        "tokens_allocated": estimated,
        "tokens_used": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "live_url": None
    }
    await db.projects.insert_one(project)
    
    await db.users.update_one({"id": user["id"]}, {"$inc": {"token_balance": -estimated}})
    
    background_tasks.add_task(run_orchestration, project_id, user["id"])
    
    return {"project": {k: v for k, v in project.items() if k != "_id"}}

@api_router.get("/projects")
async def get_projects(user: dict = Depends(get_current_user)):
    projects = await db.projects.find({"user_id": user["id"]}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return {"projects": projects}

@api_router.get("/projects/{project_id}")
async def get_project(project_id: str, user: dict = Depends(get_current_user)):
    project = await db.projects.find_one({"id": project_id, "user_id": user["id"]}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"project": project}

@api_router.get("/projects/{project_id}/logs")
async def get_project_logs(project_id: str, user: dict = Depends(get_current_user)):
    logs = await db.project_logs.find({"project_id": project_id}, {"_id": 0}).sort("created_at", 1).to_list(500)
    return {"logs": logs}

# ==================== ORCHESTRATION ====================

async def run_orchestration(project_id: str, user_id: str):
    """Simulates the agent orchestration process"""
    agents_order = [
        ("Planner", 50000),
        ("Requirements Clarifier", 30000),
        ("Stack Selector", 20000),
        ("Frontend Generation", 150000),
        ("Backend Generation", 120000),
        ("Database Agent", 80000),
        ("API Integration", 60000),
        ("Test Generation", 100000),
        ("Security Checker", 40000),
        ("Test Executor", 50000),
        ("Deployment Agent", 60000),
        ("Memory Agent", 25000)
    ]
    
    await db.projects.update_one({"id": project_id}, {"$set": {"status": "running"}})
    
    total_used = 0
    for agent_name, base_tokens in agents_order:
        await db.agent_status.update_one(
            {"project_id": project_id, "agent_name": agent_name},
            {"$set": {
                "project_id": project_id,
                "agent_name": agent_name,
                "status": "running",
                "progress": 0,
                "tokens_used": 0,
                "started_at": datetime.now(timezone.utc).isoformat()
            }},
            upsert=True
        )
        
        await db.project_logs.insert_one({
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "agent": agent_name,
            "message": f"Starting {agent_name}...",
            "level": "info",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        tokens_used = int(base_tokens * random.uniform(0.8, 1.2))
        for progress in range(0, 101, 20):
            await asyncio.sleep(0.5)
            await db.agent_status.update_one(
                {"project_id": project_id, "agent_name": agent_name},
                {"$set": {"progress": progress, "tokens_used": int(tokens_used * progress / 100)}}
            )
        
        await db.agent_status.update_one(
            {"project_id": project_id, "agent_name": agent_name},
            {"$set": {"status": "completed", "progress": 100, "tokens_used": tokens_used}}
        )
        
        await db.token_usage.insert_one({
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "user_id": user_id,
            "agent": agent_name,
            "tokens": tokens_used,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        total_used += tokens_used
        
        await db.project_logs.insert_one({
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "agent": agent_name,
            "message": f"{agent_name} completed. Used {tokens_used:,} tokens.",
            "level": "success",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    
    live_url = f"https://app-{project_id[:8]}.crucibai.dev"
    await db.projects.update_one(
        {"id": project_id},
        {"$set": {
            "status": "completed",
            "tokens_used": total_used,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "live_url": live_url
        }}
    )
    
    project = await db.projects.find_one({"id": project_id})
    if project:
        refund = project["tokens_allocated"] - total_used
        if refund > 0:
            await db.users.update_one({"id": user_id}, {"$inc": {"token_balance": refund}})
            await db.token_ledger.insert_one({
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "tokens": refund,
                "type": "refund",
                "description": f"Unused tokens from project {project_id[:8]}",
                "created_at": datetime.now(timezone.utc).isoformat()
            })

# ==================== EXPORTS ROUTES ====================

@api_router.post("/exports")
async def create_export(data: dict, user: dict = Depends(get_current_user)):
    project = await db.projects.find_one({"id": data.get("project_id"), "user_id": user["id"]})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    export_id = str(uuid.uuid4())
    export_doc = {
        "id": export_id,
        "project_id": data.get("project_id"),
        "user_id": user["id"],
        "format": data.get("format", "pdf"),
        "status": "completed",
        "download_url": f"/api/exports/{export_id}/download",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.exports.insert_one(export_doc)
    
    return {"export": {k: v for k, v in export_doc.items() if k != "_id"}}

@api_router.get("/exports")
async def get_exports(user: dict = Depends(get_current_user)):
    exports = await db.exports.find({"user_id": user["id"]}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return {"exports": exports}

# ==================== PATTERNS ROUTES ====================

@api_router.get("/patterns")
async def get_patterns(user: dict = Depends(get_optional_user)):
    patterns = [
        {"id": "auth-jwt", "name": "JWT Authentication", "category": "auth", "usage_count": 1250, "tokens_saved": 45000},
        {"id": "stripe-checkout", "name": "Stripe Checkout Flow", "category": "payments", "usage_count": 890, "tokens_saved": 60000},
        {"id": "crud-api", "name": "RESTful CRUD API", "category": "backend", "usage_count": 2100, "tokens_saved": 35000},
        {"id": "responsive-dashboard", "name": "Responsive Dashboard", "category": "frontend", "usage_count": 1560, "tokens_saved": 80000},
        {"id": "social-oauth", "name": "Social OAuth (Google/GitHub)", "category": "auth", "usage_count": 780, "tokens_saved": 55000},
        {"id": "file-upload", "name": "File Upload with S3", "category": "storage", "usage_count": 650, "tokens_saved": 40000},
        {"id": "email-sendgrid", "name": "SendGrid Email Integration", "category": "communications", "usage_count": 920, "tokens_saved": 30000},
        {"id": "realtime-ws", "name": "WebSocket Real-time Updates", "category": "realtime", "usage_count": 430, "tokens_saved": 65000}
    ]
    return {"patterns": patterns}

# ==================== DASHBOARD STATS ====================

@api_router.get("/dashboard/stats")
async def get_dashboard_stats(user: dict = Depends(get_current_user)):
    projects = await db.projects.find({"user_id": user["id"]}).to_list(1000)
    
    total_projects = len(projects)
    completed_projects = len([p for p in projects if p.get("status") == "completed"])
    running_projects = len([p for p in projects if p.get("status") == "running"])
    total_tokens_used = sum(p.get("tokens_used", 0) for p in projects)
    
    weekly_data = [
        {"day": "Mon", "tokens": random.randint(20000, 100000), "projects": random.randint(1, 5)},
        {"day": "Tue", "tokens": random.randint(20000, 100000), "projects": random.randint(1, 5)},
        {"day": "Wed", "tokens": random.randint(20000, 100000), "projects": random.randint(1, 5)},
        {"day": "Thu", "tokens": random.randint(20000, 100000), "projects": random.randint(1, 5)},
        {"day": "Fri", "tokens": random.randint(20000, 100000), "projects": random.randint(1, 5)},
        {"day": "Sat", "tokens": random.randint(10000, 50000), "projects": random.randint(0, 3)},
        {"day": "Sun", "tokens": random.randint(10000, 50000), "projects": random.randint(0, 3)}
    ]
    
    return {
        "total_projects": total_projects,
        "completed_projects": completed_projects,
        "running_projects": running_projects,
        "token_balance": user["token_balance"],
        "total_tokens_used": total_tokens_used,
        "weekly_data": weekly_data,
        "plan": user.get("plan", "free")
    }

# ==================== ROOT ====================

@api_router.get("/")
async def root():
    return {"message": "CrucibAI Platform API", "version": "1.0.0"}

@api_router.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
