# Complete Setup Guide - Medical Insight Engine (Frontend + Backend)

## 🚀 Full Stack Integration & Execution

### System Requirements
- **Node.js** 16+ (recommended 18+)
- **Python** 3.9+
- **PostgreSQL** 12+
- **Redis** 6+ (optional but recommended)
- **Git**

---

## PART 1: Backend Setup

### 1.1 Install Python Dependencies

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Download spacy models (required for NLP)
python -m spacy download en_core_web_sm
```

### 1.2 Create Backend Environment File

```bash
cd backend
cp .env.example .env  # or create new .env file
```

Edit `backend/.env`:
```env
# Application
APP_NAME=Medical Insight Engine
APP_VERSION=1.0.0
DEBUG=true
ENVIRONMENT=development

# Security (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=your-secret-key-min-32-chars-here-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENCRYPTION_KEY=your-encryption-key-min-32-chars-here-change

# Database - PostgreSQL (local)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/medical_insight

# Redis
REDIS_URL=redis://localhost:6379/0

# File Storage
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760

# CORS - Allow frontend
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000"]
CORS_ALLOW_CREDENTIALS=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Email (optional)
SMTP_SERVER=localhost
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-email-password
```

### 1.3 Set Up Database

**Option A: Using PostgreSQL locally**

```bash
# Create database
createdb medical_insight

# Or using psql
psql -U postgres
# Inside psql:
CREATE DATABASE medical_insight;
```

**Option B: Using Docker PostgreSQL**

```bash
docker run -d \
  --name postgres-medical \
  -e POSTGRES_DB=medical_insight \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:15
```

### 1.4 Run Database Migrations (if using Alembic)

```bash
cd backend
alembic upgrade head
```

### 1.5 Start Backend Server

```bash
# Make sure venv is activated
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run with uvicorn
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend is now running at: **http://localhost:8000**

Check API docs at: **http://localhost:8000/api/docs**

---

## PART 2: Frontend Setup

### 2.1 Install Node Dependencies

```bash
cd frontend
npm install
```

### 2.2 Create Frontend Environment File

```bash
cp .env.example .env
```

Edit `frontend/.env`:
```env
# API Configuration
VITE_API_URL=http://localhost:8000/api

# App Settings
VITE_APP_NAME=Medical Insight Engine
VITE_APP_VERSION=1.0.0
VITE_DEBUG=true

# Features
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_OFFLINE_MODE=false

# Storage
VITE_TOKEN_STORAGE_KEY=access_token
VITE_USER_STORAGE_KEY=user

# Logging
VITE_LOG_LEVEL=info
```

### 2.3 Fix Frontend Issues

The CSS warnings are normal but can be suppressed. Update `frontend/src/styles/global.css`:

Replace:
```css
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
```

With:
```css
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
```

### 2.4 Start Frontend Development Server

```bash
cd frontend
npm run dev
```

Frontend is now running at: **http://localhost:5173** (or http://localhost:3000)

---

## PART 3: Run Both Together

### Option A: Using Two Terminal Windows (Recommended for Development)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Option B: Using Docker Compose (Recommended for Production-like Setup)

Create `docker-compose.yml` in root directory:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: medical_insight
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.backend
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/medical_insight
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: your-secret-key-change-this
      ENCRYPTION_KEY: your-encryption-key-change-this
      DEBUG: "true"
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
      - ./uploads:/app/uploads
    command: python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ./frontend/src:/app/src
      - ./frontend/public:/app/public
    environment:
      VITE_API_URL: http://backend:8000/api
    command: npm run dev

volumes:
  postgres_data:
```

Run with Docker:
```bash
docker-compose up
```

---

## PART 4: Verify Integration

### 4.1 Test Backend API

```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Check API documentation
# Open: http://localhost:8000/api/docs
```

### 4.2 Test Frontend Connectivity

1. Open frontend: **http://localhost:5173** (or 3000)
2. Try to access login page
3. Check browser console for any errors
4. Open DevTools Network tab
5. Try login - should see requests to `http://localhost:8000/api/auth/login`

### 4.3 Test Complete Authentication Flow

```bash
# Register new user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test@123456",
    "full_name": "Test User"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test@example.com",
    "password": "Test@123456"
  }'
```

---

## PART 5: Common Issues & Solutions

### Issue: Port Already in Use

```bash
# Find and kill process on port 8000 (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8000
kill -9 <PID>
```

### Issue: Database Connection Failed

```bash
# Check if PostgreSQL is running
# Windows: Services > PostgreSQL
# macOS: brew services list
# Linux: sudo systemctl status postgresql

# Or use Docker PostgreSQL:
docker run -d -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=medical_insight \
  postgres:15
```

### Issue: Frontend Can't Connect to Backend

Check `frontend/.env`:
```
VITE_API_URL=http://localhost:8000/api
```

Check backend CORS in `backend/app/main.py`:
```python
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

### Issue: Module Not Found (Backend)

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Issue: npm install fails

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm install
```

### Issue: Vite Dev Server Not Starting

```bash
cd frontend
npm cache clean --force
npm install
npm run dev
```

---

## PART 6: Project Structure

```
medical-insight-engine/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Settings
│   │   ├── database.py          # DB setup
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── auth.py      # Auth endpoints
│   │   │   │   ├── upload.py    # Upload endpoints
│   │   │   │   ├── reports.py   # Reports endpoints
│   │   │   │   └── analytics.py # Analytics endpoints
│   │   │   └── deps.py          # Dependencies
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   ├── core/                # Core utilities
│   │   └── utils/               # Helper functions
│   ├── tests/
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile.backend
├── frontend/
│   ├── src/
│   │   ├── index.js
│   │   ├── App.jsx
│   │   ├── components/
│   │   ├── context/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── utils/
│   │   └── styles/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── .env.example
│   └── Dockerfile.frontend
├── docker-compose.yml
└── README.md
```

---

## PART 7: Development Workflow

### Local Development (Recommended)

**Terminal 1:**
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2:**
```bash
cd frontend
npm run dev
```

Access:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

### Development with Docker

```bash
# Build images
docker-compose build

# Run services
docker-compose up

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

Access:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

---

## PART 8: Production Deployment

### Build Frontend
```bash
cd frontend
npm run build
# Creates dist/ folder with optimized build
```

### Build Backend Docker Image
```bash
docker build -f backend/Dockerfile.backend -t medical-insight-backend .
```

### Deploy
Use docker-compose for production:
```bash
docker-compose -f docker-compose.prod.yml up
```

---

## PART 9: Verify Everything Works

### Step 1: Check Backend Health
```bash
curl http://localhost:8000/api/health
# Expected: {"status": "ok"}
```

### Step 2: Check Frontend
Open http://localhost:5173 in browser

### Step 3: Test API Documentation
Open http://localhost:8000/api/docs in browser

### Step 4: Test Login Flow
1. Go to http://localhost:5173/auth/register
2. Create account
3. Login with credentials
4. Should redirect to dashboard
5. Check Network tab for API calls to localhost:8000

### Step 5: Test File Upload
1. Go to /upload page
2. Drag and drop a PDF
3. Click upload
4. Should see progress and success message

---

## Quick Start Cheatsheet

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate  # or: source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
# Create .env file with DATABASE_URL
python -m uvicorn app.main:app --reload

# Frontend (in new terminal)
cd frontend
npm install
# Create .env with VITE_API_URL=http://localhost:8000/api
npm run dev
```

Open:
- Frontend: http://localhost:5173
- Backend Docs: http://localhost:8000/api/docs

---

## Troubleshooting Summary

| Issue | Solution |
|-------|----------|
| Port in use | `netstat -ano \| findstr :8000` then `taskkill /PID <ID> /F` |
| DB connection failed | Check PostgreSQL running, verify DATABASE_URL |
| CORS error | Check CORS_ORIGINS in backend config |
| Can't login | Verify backend running, check API URL in frontend |
| Module not found | Run `pip install -r requirements.txt` |
| npm install fails | `npm cache clean --force && npm install` |
| Styling issues | Check Tailwind CSS is processing (restart `npm run dev`) |

---

## Next Steps

1. ✅ Backend running on :8000
2. ✅ Frontend running on :5173
3. ✅ Database configured
4. ✅ API documentation at /api/docs
5. Ready for development!

For issues, check the documentation in each folder or see troubleshooting above.
