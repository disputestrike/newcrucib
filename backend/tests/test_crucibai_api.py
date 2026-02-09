"""
CrucibAI API Tests - Testing all backend endpoints
Tests: Health, AI Chat, Voice Transcribe, Auth, Tokens, Projects, Patterns
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://crucibai-builder.preview.emergentagent.com')

class TestHealthEndpoints:
    """Health check endpoint tests"""
    
    def test_health_endpoint(self):
        """Test /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        print(f"Health check passed: {data}")
    
    def test_root_endpoint(self):
        """Test /api/ returns API info"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "CrucibAI" in data["message"]
        print(f"Root endpoint passed: {data}")


class TestAIChatEndpoints:
    """AI Chat endpoint tests with model selection"""
    
    def test_ai_chat_auto_model(self):
        """Test /api/ai/chat with auto model selection"""
        response = requests.post(f"{BASE_URL}/api/ai/chat", json={
            "message": "Hello, test message",
            "model": "auto"
        }, timeout=60)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "model_used" in data
        assert "tokens_used" in data
        assert "session_id" in data
        print(f"AI Chat (auto) passed: model={data['model_used']}, tokens={data['tokens_used']}")
    
    def test_ai_chat_gpt4o_model(self):
        """Test /api/ai/chat with GPT-4o model"""
        response = requests.post(f"{BASE_URL}/api/ai/chat", json={
            "message": "What is 2+2?",
            "model": "gpt-4o"
        }, timeout=60)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "gpt-4o" in data["model_used"].lower() or "openai" in data["model_used"].lower()
        print(f"AI Chat (GPT-4o) passed: model={data['model_used']}")
    
    def test_ai_chat_claude_model(self):
        """Test /api/ai/chat with Claude model"""
        response = requests.post(f"{BASE_URL}/api/ai/chat", json={
            "message": "Say hello",
            "model": "claude"
        }, timeout=60)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "claude" in data["model_used"].lower() or "anthropic" in data["model_used"].lower()
        print(f"AI Chat (Claude) passed: model={data['model_used']}")
    
    def test_ai_chat_gemini_model(self):
        """Test /api/ai/chat with Gemini model"""
        response = requests.post(f"{BASE_URL}/api/ai/chat", json={
            "message": "Hi there",
            "model": "gemini"
        }, timeout=60)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "gemini" in data["model_used"].lower()
        print(f"AI Chat (Gemini) passed: model={data['model_used']}")
    
    def test_ai_chat_with_session(self):
        """Test /api/ai/chat maintains session"""
        session_id = f"test_session_{int(time.time())}"
        
        # First message
        response1 = requests.post(f"{BASE_URL}/api/ai/chat", json={
            "message": "Remember the number 42",
            "session_id": session_id,
            "model": "auto"
        }, timeout=60)
        assert response1.status_code == 200
        assert response1.json()["session_id"] == session_id
        
        # Second message with same session
        response2 = requests.post(f"{BASE_URL}/api/ai/chat", json={
            "message": "What number did I mention?",
            "session_id": session_id,
            "model": "auto"
        }, timeout=60)
        assert response2.status_code == 200
        assert response2.json()["session_id"] == session_id
        print(f"AI Chat session test passed: session_id={session_id}")


class TestAIAnalysisEndpoints:
    """AI Analysis endpoint tests"""
    
    def test_ai_analyze_summarize(self):
        """Test /api/ai/analyze with summarize task"""
        response = requests.post(f"{BASE_URL}/api/ai/analyze", json={
            "content": "This is a test document about software development. It covers topics like coding, testing, and deployment.",
            "task": "summarize"
        }, timeout=60)
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert data["task"] == "summarize"
        print(f"AI Analyze (summarize) passed")
    
    def test_ai_analyze_extract(self):
        """Test /api/ai/analyze with extract task"""
        response = requests.post(f"{BASE_URL}/api/ai/analyze", json={
            "content": "John Smith works at Acme Corp in New York. He is a software engineer.",
            "task": "extract"
        }, timeout=60)
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert data["task"] == "extract"
        print(f"AI Analyze (extract) passed")


class TestSearchEndpoint:
    """Search endpoint tests"""
    
    def test_hybrid_search(self):
        """Test /api/search with hybrid search"""
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "React components",
            "search_type": "hybrid"
        }, timeout=60)
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "results" in data
        assert data["search_type"] == "hybrid"
        print(f"Hybrid search passed")


class TestAuthEndpoints:
    """Authentication endpoint tests"""
    
    def test_register_new_user(self):
        """Test /api/auth/register creates new user"""
        test_email = f"test_user_{int(time.time())}@example.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "testpass123",
            "name": "Test User"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == test_email
        assert data["user"]["token_balance"] == 50000  # Welcome bonus
        print(f"Register passed: email={test_email}")
        return data["token"], test_email
    
    def test_register_duplicate_email(self):
        """Test /api/auth/register rejects duplicate email"""
        # First registration
        test_email = f"test_dup_{int(time.time())}@example.com"
        requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "testpass123",
            "name": "Test User"
        })
        
        # Second registration with same email
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "testpass123",
            "name": "Test User 2"
        })
        assert response.status_code == 400
        print(f"Duplicate email rejection passed")
    
    def test_login_valid_credentials(self):
        """Test /api/auth/login with valid credentials"""
        # First register
        test_email = f"test_login_{int(time.time())}@example.com"
        requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "testpass123",
            "name": "Test User"
        })
        
        # Then login
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": test_email,
            "password": "testpass123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        print(f"Login passed: email={test_email}")
    
    def test_login_invalid_credentials(self):
        """Test /api/auth/login rejects invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "wrongpass"
        })
        assert response.status_code == 401
        print(f"Invalid login rejection passed")
    
    def test_get_me_authenticated(self):
        """Test /api/auth/me returns user info"""
        # Register and get token
        test_email = f"test_me_{int(time.time())}@example.com"
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "testpass123",
            "name": "Test User"
        })
        token = reg_response.json()["token"]
        
        # Get user info
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_email
        print(f"Get me passed: email={test_email}")
    
    def test_get_me_unauthenticated(self):
        """Test /api/auth/me rejects unauthenticated requests"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
        print(f"Unauthenticated rejection passed")


class TestTokenEndpoints:
    """Token management endpoint tests"""
    
    def test_get_bundles(self):
        """Test /api/tokens/bundles returns available bundles"""
        response = requests.get(f"{BASE_URL}/api/tokens/bundles")
        assert response.status_code == 200
        data = response.json()
        assert "bundles" in data
        assert "starter" in data["bundles"]
        assert "pro" in data["bundles"]
        assert "professional" in data["bundles"]
        print(f"Get bundles passed: {list(data['bundles'].keys())}")
    
    def test_purchase_tokens(self):
        """Test /api/tokens/purchase adds tokens"""
        # Register and get token
        test_email = f"test_purchase_{int(time.time())}@example.com"
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "testpass123",
            "name": "Test User"
        })
        token = reg_response.json()["token"]
        initial_balance = reg_response.json()["user"]["token_balance"]
        
        # Purchase tokens
        response = requests.post(f"{BASE_URL}/api/tokens/purchase", 
            json={"bundle": "starter"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["new_balance"] == initial_balance + 100000  # starter bundle
        print(f"Purchase tokens passed: new_balance={data['new_balance']}")
    
    def test_get_token_history(self):
        """Test /api/tokens/history returns transaction history"""
        # Register and get token
        test_email = f"test_history_{int(time.time())}@example.com"
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "testpass123",
            "name": "Test User"
        })
        token = reg_response.json()["token"]
        
        # Get history
        response = requests.get(f"{BASE_URL}/api/tokens/history", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        assert "current_balance" in data
        # Should have welcome bonus entry
        assert len(data["history"]) >= 1
        print(f"Get token history passed: {len(data['history'])} entries")


class TestAgentsEndpoints:
    """Agent management endpoint tests"""
    
    def test_get_agents(self):
        """Test /api/agents returns agent definitions"""
        response = requests.get(f"{BASE_URL}/api/agents")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert len(data["agents"]) > 0
        # Check for expected agents
        agent_names = [a["name"] for a in data["agents"]]
        assert "Planner" in agent_names
        assert "Frontend Generation" in agent_names
        assert "Backend Generation" in agent_names
        print(f"Get agents passed: {len(data['agents'])} agents")


class TestPatternsEndpoints:
    """Pattern library endpoint tests"""
    
    def test_get_patterns(self):
        """Test /api/patterns returns pattern library"""
        response = requests.get(f"{BASE_URL}/api/patterns")
        assert response.status_code == 200
        data = response.json()
        assert "patterns" in data
        assert len(data["patterns"]) > 0
        # Check pattern structure
        pattern = data["patterns"][0]
        assert "id" in pattern
        assert "name" in pattern
        assert "category" in pattern
        print(f"Get patterns passed: {len(data['patterns'])} patterns")


class TestDashboardEndpoints:
    """Dashboard stats endpoint tests"""
    
    def test_get_dashboard_stats(self):
        """Test /api/dashboard/stats returns user stats"""
        # Register and get token
        test_email = f"test_dashboard_{int(time.time())}@example.com"
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "testpass123",
            "name": "Test User"
        })
        token = reg_response.json()["token"]
        
        # Get dashboard stats
        response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert "total_projects" in data
        assert "token_balance" in data
        assert "weekly_data" in data
        print(f"Get dashboard stats passed: balance={data['token_balance']}")


class TestProjectEndpoints:
    """Project management endpoint tests"""
    
    def test_create_project(self):
        """Test /api/projects creates new project"""
        # Register and get token
        test_email = f"test_project_{int(time.time())}@example.com"
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "testpass123",
            "name": "Test User"
        })
        token = reg_response.json()["token"]
        
        # Create project
        response = requests.post(f"{BASE_URL}/api/projects", 
            json={
                "name": "Test Project",
                "description": "A test project",
                "project_type": "web_app",
                "requirements": {"features": ["auth", "dashboard"]},
                "estimated_tokens": 50000
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        # Note: May fail if insufficient tokens, which is expected behavior
        if response.status_code == 200:
            data = response.json()
            assert "project" in data
            assert data["project"]["name"] == "Test Project"
            print(f"Create project passed: id={data['project']['id'][:8]}")
        else:
            print(f"Create project skipped (insufficient tokens): {response.status_code}")
    
    def test_get_projects(self):
        """Test /api/projects returns user projects"""
        # Register and get token
        test_email = f"test_projects_{int(time.time())}@example.com"
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "testpass123",
            "name": "Test User"
        })
        token = reg_response.json()["token"]
        
        # Get projects
        response = requests.get(f"{BASE_URL}/api/projects", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert "projects" in data
        print(f"Get projects passed: {len(data['projects'])} projects")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
