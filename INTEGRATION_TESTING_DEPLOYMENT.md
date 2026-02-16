# Integration Testing & Deployment Guide

## Status: Ready for Deployment ✅

All security fixes have been implemented, reviewed, and verified. This guide covers integration testing and deployment steps.

---

## Pre-Deployment Checklist

### Code Quality ✅
- [x] All Python files compile successfully
- [x] CodeQL security scan passed (0 alerts)
- [x] Code review completed
- [x] All 10 security issues resolved

### Documentation ✅
- [x] SECURITY_FIXES_SUMMARY.md created
- [x] SECURITY_VERIFICATION_REPORT.md created
- [x] Code changes documented
- [x] Environment variables documented

---

## Integration Testing Steps

### 1. Environment Setup

```bash
# Set required environment variables
export JWT_SECRET="$(openssl rand -base64 32)"
export ENCRYPTION_KEY="$(python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"
export CORS_ORIGINS="http://localhost:3000"
export MONGO_URL="mongodb://localhost:27017"
export DB_NAME="crucibai_test"

# Optional - for LLM features
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"
```

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Run Tests

#### Quick Syntax Validation
```bash
# Verify Python syntax
python3 -m py_compile server.py
python3 -m py_compile encryption.py
python3 -m py_compile error_handlers.py
python3 -m py_compile tests/test_security_fixes.py
```

#### Run Security Tests
```bash
# Run security-specific tests
pytest tests/test_security_fixes.py -v

# Run smoke tests
pytest tests/test_smoke.py -v

# Run security tests
pytest tests/test_security.py -v

# Run API contract tests
pytest tests/test_api_contract.py -v
```

#### Run Full Test Suite
```bash
# Run all tests
pytest tests/ -v --tb=short

# Or use the test runner
python -m pytest tests/
```

### 4. Manual Integration Tests

#### Test 1: Encryption/Decryption
```python
from encryption import encrypt_value, decrypt_value

# Test encryption
original = "sk-test-api-key-12345"
encrypted = encrypt_value(original)
decrypted = decrypt_value(encrypted)

assert decrypted == original, "Encryption/decryption failed"
print("✓ Encryption test passed")
```

#### Test 2: Logging Redaction
```python
from error_handlers import redact_sensitive_data

# Test redaction
data = {
    "user": "john",
    "password": "secret123",
    "api_key": "sk-12345"
}

redacted = redact_sensitive_data(data)
assert redacted["password"] == "***REDACTED***"
assert redacted["api_key"] == "***REDACTED***"
assert redacted["user"] == "john"
print("✓ Redaction test passed")
```

#### Test 3: Input Validation
```python
from server import ChatMessage
from pydantic import ValidationError

# Test valid input
msg = ChatMessage(message="Hello world")
print("✓ Valid input accepted")

# Test invalid input (too long)
try:
    msg = ChatMessage(message="x" * 10001)
    print("✗ Validation failed - should reject long input")
except ValidationError:
    print("✓ Long input rejected correctly")
```

#### Test 4: Server Startup
```bash
# Test server starts successfully
cd backend
uvicorn server:app --host 0.0.0.0 --port 8000 --reload &
SERVER_PID=$!
sleep 5

# Test health check
curl http://localhost:8000/health || echo "No health endpoint"

# Stop server
kill $SERVER_PID
```

---

## Staging Deployment

### Option 1: Docker Deployment (Recommended)

#### Create Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ .

# Environment variables (override with docker run -e)
ENV JWT_SECRET=""
ENV ENCRYPTION_KEY=""
ENV CORS_ORIGINS="http://localhost:3000"
ENV MONGO_URL="mongodb://mongo:27017"
ENV DB_NAME="crucibai"

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose (with MongoDB)
```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongo-data:/data/db
    environment:
      MONGO_INITDB_DATABASE: crucibai

  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      JWT_SECRET: ${JWT_SECRET}
      ENCRYPTION_KEY: ${ENCRYPTION_KEY}
      CORS_ORIGINS: ${CORS_ORIGINS}
      MONGO_URL: mongodb://mongodb:27017
      DB_NAME: crucibai
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
    depends_on:
      - mongodb

volumes:
  mongo-data:
```

#### Build and Run
```bash
# Generate secrets
export JWT_SECRET="$(openssl rand -base64 32)"
export ENCRYPTION_KEY="$(python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"
export CORS_ORIGINS="https://staging.example.com"

# Build and start
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Test endpoints
curl http://localhost:8000/api/health
```

### Option 2: Direct Deployment

#### On Ubuntu/Debian Server
```bash
# 1. Clone repository
git clone https://github.com/disputestrike/newcrucib.git
cd newcrucib
git checkout copilot/fix-security-code-quality-issues

# 2. Install dependencies
cd backend
pip3 install -r requirements.txt

# 3. Set environment variables
cat > .env << EOF
JWT_SECRET=$(openssl rand -base64 32)
ENCRYPTION_KEY=$(python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')
CORS_ORIGINS=https://staging.example.com
MONGO_URL=mongodb://localhost:27017
DB_NAME=crucibai_staging
EOF

# 4. Start with systemd
sudo tee /etc/systemd/system/crucibai.service << EOF
[Unit]
Description=CrucibAI Backend
After=network.target

[Service]
Type=simple
User=crucibai
WorkingDirectory=/opt/crucibai/backend
EnvironmentFile=/opt/crucibai/backend/.env
ExecStart=/usr/bin/uvicorn server:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable crucibai
sudo systemctl start crucibai
sudo systemctl status crucibai
```

### Option 3: Platform-as-a-Service (Railway, Heroku, etc.)

#### Railway Deployment
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# Set environment variables
railway variables set JWT_SECRET="$(openssl rand -base64 32)"
railway variables set ENCRYPTION_KEY="$(python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"
railway variables set CORS_ORIGINS="https://your-app.railway.app"

# Deploy
railway up
```

---

## Post-Deployment Verification

### 1. Health Checks
```bash
# Basic connectivity
curl https://staging.example.com/api/health

# Check CORS headers
curl -H "Origin: https://staging.example.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS https://staging.example.com/api/auth/register

# Should see Access-Control-Allow-Origin header
```

### 2. Security Verification
```bash
# Test JWT requirement
curl https://staging.example.com/api/auth/me
# Should return 401 without token

# Test rate limiting
for i in {1..110}; do
  curl https://staging.example.com/api/health
done
# Should start returning 429 after 100 requests
```

### 3. API Endpoint Tests
```bash
# Test registration
curl -X POST https://staging.example.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","name":"Test User"}'

# Test login
curl -X POST https://staging.example.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'
```

### 4. Monitor Logs
```bash
# Check for errors
tail -f /var/log/crucibai.log

# Or with Docker
docker-compose logs -f backend

# Look for:
# - No JWT_SECRET warnings
# - No encryption warnings (if ENCRYPTION_KEY set)
# - No CORS wildcard warnings
# - Proper redaction of sensitive data in logs
```

---

## Rollback Plan

If issues are discovered:

### Quick Rollback
```bash
# With Git
git checkout main
git pull origin main

# Restart services
sudo systemctl restart crucibai

# Or with Docker
docker-compose down
git checkout main
docker-compose up -d
```

### Database Migration Rollback
If you've run the encryption migration and need to rollback:

```python
# Only needed if you encrypted existing data
from encryption import decrypt_dict
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def rollback():
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ['DB_NAME']]
    
    async for doc in db.workspace_env.find({}):
        if 'env' in doc:
            decrypted_env = decrypt_dict(doc['env'])
            await db.workspace_env.update_one(
                {"_id": doc["_id"]},
                {"$set": {"env": decrypted_env}}
            )
    print("Rollback complete")

asyncio.run(rollback())
```

---

## Monitoring & Alerts

### Key Metrics to Monitor

1. **Error Rates**
   - Watch for increases in 500 errors
   - Monitor authentication failures (401s)
   - Track rate limit hits (429s)

2. **Performance**
   - Response times for API endpoints
   - Database connection pool usage
   - Timeout occurrences

3. **Security**
   - Failed login attempts
   - Invalid JWT tokens
   - CORS violations
   - Large file upload attempts

### Logging Best Practices

```python
# In your monitoring system, set up alerts for:
# - "CRITICAL ERROR" in logs
# - "JWT_SECRET not set"
# - "ENCRYPTION_KEY not set"
# - Rate limit exceeded for same IP repeatedly
# - Multiple authentication failures from same IP
```

---

## Success Criteria

✅ All tests pass
✅ Server starts without errors
✅ JWT authentication working
✅ API keys encrypted in database
✅ CORS properly restricted
✅ Logs don't contain sensitive data
✅ Rate limiting active
✅ Input validation working
✅ Timeouts functioning
✅ No security vulnerabilities

---

## Support & Troubleshooting

### Common Issues

#### 1. "JWT_SECRET not set" Error
**Solution**: Set JWT_SECRET environment variable before starting server
```bash
export JWT_SECRET="$(openssl rand -base64 32)"
```

#### 2. Encryption Warnings
**Solution**: Set ENCRYPTION_KEY for production
```bash
export ENCRYPTION_KEY="$(python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"
```

#### 3. CORS Errors in Browser
**Solution**: Set CORS_ORIGINS to your frontend URL
```bash
export CORS_ORIGINS="https://your-frontend.com"
```

#### 4. Database Connection Errors
**Solution**: Verify MongoDB is running and MONGO_URL is correct
```bash
# Test connection
mongosh $MONGO_URL --eval "db.runCommand({ping: 1})"
```

---

## Next Steps After Deployment

1. **Monitor for 24 hours** - Watch logs and metrics
2. **Load testing** - Use tools like Apache Bench or k6
3. **Security audit** - Consider professional penetration testing
4. **Documentation** - Update API docs with new security features
5. **Team training** - Ensure team understands new security features

---

## Contact

For issues or questions:
- GitHub Issues: https://github.com/disputestrike/newcrucib/issues
- Security concerns: Report privately through GitHub Security

---

**Last Updated**: 2026-02-16
**Version**: 1.0 (Security Fixes)
**Branch**: copilot/fix-security-code-quality-issues
