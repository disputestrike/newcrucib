import requests
import sys
import json
from datetime import datetime
import time

class AgentForgeAPITester:
    def __init__(self, base_url="https://construct-zone-11.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.project_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, data=None, auth_required=True):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if auth_required and self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json() if response.content else {}
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                self.failed_tests.append({
                    'name': name,
                    'expected': expected_status,
                    'actual': response.status_code,
                    'response': response.text[:200]
                })
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append({
                'name': name,
                'error': str(e)
            })
            return False, {}

    def test_health_endpoints(self):
        """Test basic health endpoints"""
        print("\n=== TESTING HEALTH ENDPOINTS ===")
        
        # Test root endpoint
        self.run_test("API Root", "GET", "", 200, auth_required=False)
        
        # Test health endpoint
        self.run_test("Health Check", "GET", "health", 200, auth_required=False)

    def test_auth_flow(self):
        """Test complete authentication flow"""
        print("\n=== TESTING AUTHENTICATION ===")
        
        # Generate unique test user
        timestamp = int(time.time())
        test_email = f"test_user_{timestamp}@example.com"
        test_password = "TestPass123!"
        test_name = f"Test User {timestamp}"
        
        # Test registration
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data={
                "email": test_email,
                "password": test_password,
                "name": test_name
            },
            auth_required=False
        )
        
        if success and 'token' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            print(f"   Token obtained: {self.token[:20]}...")
        
        # Test login with same credentials
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data={
                "email": test_email,
                "password": test_password
            },
            auth_required=False
        )
        
        # Test get current user
        if self.token:
            self.run_test("Get Current User", "GET", "auth/me", 200)
        
        # Test invalid login
        self.run_test(
            "Invalid Login",
            "POST",
            "auth/login",
            401,
            data={
                "email": test_email,
                "password": "wrongpassword"
            },
            auth_required=False
        )

    def test_token_endpoints(self):
        """Test token-related endpoints"""
        print("\n=== TESTING TOKEN ENDPOINTS ===")
        
        # Test get token bundles
        self.run_test("Get Token Bundles", "GET", "tokens/bundles", 200, auth_required=False)
        
        if not self.token:
            print("⚠️  Skipping authenticated token tests - no auth token")
            return
        
        # Test token history
        self.run_test("Get Token History", "GET", "tokens/history", 200)
        
        # Test token usage
        self.run_test("Get Token Usage", "GET", "tokens/usage", 200)
        
        # Test token purchase (simulated) - buy pro bundle for more tokens
        self.run_test(
            "Purchase Tokens",
            "POST",
            "tokens/purchase",
            200,
            data={"bundle": "pro"}
        )

    def test_agent_endpoints(self):
        """Test agent-related endpoints"""
        print("\n=== TESTING AGENT ENDPOINTS ===")
        
        # Test get agents list
        self.run_test("Get Agents List", "GET", "agents", 200, auth_required=False)
        
        if self.project_id:
            # Test get agent status for project
            self.run_test("Get Agent Status", "GET", f"agents/status/{self.project_id}", 200)

    def test_project_endpoints(self):
        """Test project-related endpoints"""
        print("\n=== TESTING PROJECT ENDPOINTS ===")
        
        if not self.token:
            print("⚠️  Skipping project tests - no auth token")
            return
        
        # Test get projects (empty initially)
        self.run_test("Get Projects List", "GET", "projects", 200)
        
        # Test create project
        success, response = self.run_test(
            "Create Project",
            "POST",
            "projects",
            200,
            data={
                "name": "Test Project",
                "description": "A test project for API validation",
                "project_type": "website",
                "requirements": {
                    "features": ["responsive", "modern"],
                    "styling": "modern",
                    "auth": False,
                    "database": True,
                    "deployment": "vercel"
                },
                "estimated_tokens": 400000
            }
        )
        
        if success and 'project' in response:
            self.project_id = response['project']['id']
            print(f"   Project created: {self.project_id}")
            
            # Test get specific project
            self.run_test("Get Project Details", "GET", f"projects/{self.project_id}", 200)
            
            # Test get project logs
            self.run_test("Get Project Logs", "GET", f"projects/{self.project_id}/logs", 200)
            
            # Wait a bit for orchestration to start
            print("   Waiting 3 seconds for orchestration to start...")
            time.sleep(3)

    def test_dashboard_endpoints(self):
        """Test dashboard-related endpoints"""
        print("\n=== TESTING DASHBOARD ENDPOINTS ===")
        
        if not self.token:
            print("⚠️  Skipping dashboard tests - no auth token")
            return
        
        # Test dashboard stats
        self.run_test("Get Dashboard Stats", "GET", "dashboard/stats", 200)

    def test_pattern_endpoints(self):
        """Test pattern library endpoints"""
        print("\n=== TESTING PATTERN ENDPOINTS ===")
        
        if not self.token:
            print("⚠️  Skipping pattern tests - no auth token")
            return
        
        # Test get patterns
        self.run_test("Get Patterns Library", "GET", "patterns", 200)

    def test_export_endpoints(self):
        """Test export-related endpoints"""
        print("\n=== TESTING EXPORT ENDPOINTS ===")
        
        if not self.token:
            print("⚠️  Skipping export tests - no auth token")
            return
        
        # Test get exports list
        self.run_test("Get Exports List", "GET", "exports", 200)
        
        if self.project_id:
            # Test create export
            self.run_test(
                "Create Export",
                "POST",
                "exports",
                200,
                data={
                    "project_id": self.project_id,
                    "format": "pdf",
                    "include_images": True
                }
            )

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting AgentForge API Tests")
        print(f"Base URL: {self.base_url}")
        
        # Run tests in logical order
        self.test_health_endpoints()
        self.test_auth_flow()
        self.test_token_endpoints()
        self.test_agent_endpoints()
        self.test_project_endpoints()
        self.test_dashboard_endpoints()
        self.test_pattern_endpoints()
        self.test_export_endpoints()
        
        # Final agent status check if we have a project
        if self.project_id:
            print("\n=== FINAL AGENT STATUS CHECK ===")
            self.run_test("Final Agent Status", "GET", f"agents/status/{self.project_id}", 200)
        
        # Print summary
        print(f"\n📊 TEST SUMMARY")
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_run - self.tests_passed}")
        print(f"Success rate: {(self.tests_passed / self.tests_run * 100):.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                error_msg = test.get('error', f"Expected {test.get('expected')}, got {test.get('actual')}")
                print(f"  - {test['name']}: {error_msg}")
        
        return self.tests_passed == self.tests_run

def main():
    tester = AgentForgeAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())