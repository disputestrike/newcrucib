# CrucibAI Deployment Guide

## Prerequisites

- Node.js 18+
- Python 3.11+
- MongoDB 5.0+
- Docker (optional)

## Environment Setup

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create `.env` file:

```
MONGO_URL=mongodb://localhost:27017
JWT_SECRET=your_secret_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GROQ_API_KEY=your_groq_key
STRIPE_API_KEY=your_stripe_key
```

### 2. Frontend Setup

```bash
cd frontend
npm install
```

Create `.env.local` file:

```
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=CrucibAI
```

## Running Locally

### Start Backend

```bash
cd backend
python3 server.py
```

Backend will be available at `http://localhost:8000`

### Start Frontend

```bash
cd frontend
npm run dev
```

Frontend will be available at `http://localhost:5173`

## Docker Deployment

### Build Docker Images

```bash
# Backend
docker build -t crucibai-backend:latest ./backend

# Frontend
docker build -t crucibai-frontend:latest ./frontend
```

### Run with Docker Compose

```bash
docker-compose up -d
```

## Production Deployment

### 1. Build for Production

```bash
# Frontend
cd frontend
npm run build

# Backend
cd backend
pip install gunicorn
```

### 2. Deploy Backend

Using Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 server:app
```

### 3. Deploy Frontend

Using a static file server:

```bash
# Using Node.js
npm install -g serve
serve -s dist -l 3000

# Using Nginx
# Copy dist/ to /var/www/crucibai
# Configure Nginx to serve static files
```

### 4. Environment Variables

Set production environment variables:

```bash
export MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/crucibai
export JWT_SECRET=<strong_random_key>
export NODE_ENV=production
```

### 5. SSL/TLS

Use Let's Encrypt for free SSL certificates:

```bash
certbot certonly --standalone -d api.crucibai.com
```

### 6. Database Backups

Set up automated MongoDB backups:

```bash
mongodump --uri "mongodb+srv://user:pass@cluster.mongodb.net/crucibai" --out /backups/$(date +%Y%m%d)
```

## Monitoring

### Health Checks

```bash
curl http://localhost:8000/api/health
```

### Logs

Monitor application logs:

```bash
# Backend logs
tail -f backend/logs/app.log

# Frontend logs
# Check browser console
```

### Performance Metrics

Monitor key metrics:
- API response times
- Database query performance
- Frontend bundle size
- Error rates

## Scaling

### Horizontal Scaling

1. Deploy multiple backend instances
2. Use load balancer (Nginx, HAProxy)
3. Use MongoDB replica set for high availability

### Vertical Scaling

1. Increase server resources (CPU, RAM)
2. Optimize database indexes
3. Enable caching (Redis)

## Troubleshooting

### Backend Won't Start

1. Check MongoDB connection: `mongosh mongodb://localhost:27017`
2. Check environment variables: `env | grep MONGO`
3. Check logs: `tail -f backend/logs/app.log`

### Frontend Build Fails

1. Clear node_modules: `rm -rf node_modules && npm install`
2. Clear cache: `npm cache clean --force`
3. Check Node version: `node --version` (should be 18+)

### Database Connection Issues

1. Check MongoDB is running: `ps aux | grep mongod`
2. Check connection string in .env
3. Check firewall rules

## Security Checklist

- [ ] Change default JWT_SECRET
- [ ] Enable HTTPS/SSL
- [ ] Set strong database passwords
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Set up firewall rules
- [ ] Enable database backups
- [ ] Monitor for suspicious activity
- [ ] Keep dependencies updated
- [ ] Use environment variables for secrets

## Support

For deployment issues, contact support@crucibai.com
