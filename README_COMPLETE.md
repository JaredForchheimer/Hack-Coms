# 🤟 ASL Article Summarizer - Complete Setup Guide

## 🎯 Overview

The ASL Article Summarizer is a full-stack web application that:
- **Extracts content** from articles and videos
- **Validates content** using AI (Claude)
- **Generates summaries** automatically
- **Stores data** in PostgreSQL database
- **Provides ASL translations** (future feature)

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  Flask Backend  │    │   PostgreSQL    │
│   (Port 5173)   │◄──►│   (Port 5000)   │◄──►│    Database     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
   Navigation UI          API Endpoints           Database Handler
   Authentication         Claude Service          CRUD Operations
   File Upload           Content Processing       Data Validation
```

## 🚀 Quick Start (Recommended)

### Option 1: Automated Setup
```bash
# Run the automated startup script
python start_application.py
```

This script will:
- ✅ Check all prerequisites
- ✅ Install dependencies
- ✅ Initialize database
- ✅ Start both servers
- ✅ Open the application

### Option 2: Manual Setup
Follow the detailed steps below if you prefer manual control.

## 📋 Prerequisites

### Required Software
- **Python 3.8+** - [Download](https://python.org)
- **Node.js 16+** - [Download](https://nodejs.org)
- **PostgreSQL 12+** - [Download](https://postgresql.org)

### Required API Keys
- **Anthropic Claude API Key** - [Get from console.anthropic.com](https://console.anthropic.com)

## 🔧 Manual Setup Steps

### 1. Database Setup

**Start PostgreSQL:**
```bash
# Ubuntu/Debian
sudo systemctl start postgresql

# macOS (Homebrew)
brew services start postgresql

# Windows - Start PostgreSQL service
```

**Create Database:**
```bash
# Connect as postgres user
sudo -u postgres createdb asl_summarizer

# Or using psql
psql -U postgres -c "CREATE DATABASE asl_summarizer;"
```

**Initialize Schema:**
```bash
python database_handler/scripts/init_db.py
```

### 2. Backend Setup

**Navigate to backend:**
```bash
cd backend
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Configure environment:**
```bash
cp .env.example .env
# Edit .env file with your settings
```

**Required .env variables:**
```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=asl_summarizer
DB_USER=postgres
DB_PASSWORD=your_password

# API Keys
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# CORS
FRONTEND_URL=http://localhost:5173
```

**Start backend:**
```bash
python run.py
```

### 3. Frontend Setup

**Navigate to frontend:**
```bash
cd asl-summarizer-frontend
```

**Install dependencies:**
```bash
npm install
```

**Start frontend:**
```bash
npm run dev
```

## 🧪 Testing the Application

### 1. Access the Application
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:5000
- **Health Check:** http://localhost:5000/health/

### 2. Verify Integration
```bash
# Test backend health
curl http://localhost:5000/health/

# Expected response:
{
  "status": "healthy",
  "services": {
    "database": "up",
    "claude_api": "configured",
    "flask": "up"
  }
}
```

### 3. Test Features
1. **Homepage** - Should load without login (development mode)
2. **Sources Page** - Upload and process content
3. **Summaries Page** - View generated summaries
4. **Navigation** - All links should work

## 🔍 Troubleshooting

### Common Issues

**❌ Blank White Page**
- **FIXED:** Development mode now bypasses authentication
- Frontend should load immediately

**❌ Database Connection Failed**
```bash
# Check PostgreSQL status
pg_isready

# Restart PostgreSQL
sudo systemctl restart postgresql

# Check credentials in backend/.env
```

**❌ CORS Errors**
```bash
# Verify CORS settings in backend/.env
FRONTEND_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:5173
```

**❌ Missing Dependencies**
```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend
cd asl-summarizer-frontend && npm install
```

### Debug Tools

**Check Logs:**
- **Frontend:** Browser console (F12)
- **Backend:** Terminal output
- **Database:** PostgreSQL logs

**Test Endpoints:**
```bash
# Health check
curl http://localhost:5000/health/

# Sources
curl http://localhost:5000/api/sources

# Statistics
curl http://localhost:5000/api/statistics
```

## 📁 Project Structure

```
asl-summarizer/
├── 📁 asl-summarizer-frontend/     # React frontend
│   ├── src/
│   │   ├── components/             # Reusable components
│   │   ├── pages/                  # Page components
│   │   ├── context/                # React context
│   │   └── services/               # API services
│   └── package.json
├── 📁 backend/                     # Flask backend
│   ├── app/
│   │   ├── routes/                 # API endpoints
│   │   ├── services/               # Business logic
│   │   └── utils/                  # Utilities
│   ├── run.py                      # Application entry
│   └── .env                        # Configuration
├── 📁 database_handler/            # Database layer
│   ├── models/                     # Data models
│   ├── core/                       # Core functionality
│   ├── config/                     # Configuration
│   └── scripts/                    # Database scripts
├── 📄 start_application.py         # Automated startup
├── 📄 TROUBLESHOOTING_GUIDE.md     # Detailed troubleshooting
└── 📄 README_COMPLETE.md           # This file
```

## 🎯 Key Features

### ✅ Implemented Features
- **Database Handler** - Complete PostgreSQL integration
- **Content Processing** - URL and file upload support
- **AI Validation** - Claude-powered content validation
- **Summary Generation** - Automated summarization
- **Data Storage** - Persistent storage with relationships
- **Web Interface** - Full React frontend
- **API Integration** - RESTful backend APIs

### 🔄 Development Mode Features
- **Authentication Bypass** - No login required for testing
- **Mock Data** - Automatic user creation
- **Hot Reload** - Frontend updates automatically
- **Debug Logging** - Detailed console output

### 🚧 Future Features
- **ASL Video Generation** - Convert summaries to ASL
- **User Authentication** - Real user management
- **Community Sharing** - Share ASL videos
- **Advanced Search** - Full-text search capabilities

## 🔐 Security Notes

### Development Mode
- Authentication is **bypassed** for development
- Mock users are **automatically created**
- API keys should be kept **secure**

### Production Deployment
- Enable **real authentication**
- Use **environment variables** for secrets
- Configure **proper CORS** settings
- Set up **SSL/HTTPS**

## 📚 API Documentation

### Health Endpoints
- `GET /health/` - Overall health check
- `GET /health/database` - Database status
- `GET /health/claude` - Claude API status

### Content Processing
- `POST /api/media/extract-url` - Extract from URL
- `POST /api/media/process-file` - Process uploaded file
- `POST /api/media/validate` - Validate content
- `POST /api/media/summarize` - Generate summary

### Data Retrieval
- `GET /api/sources` - Get all sources
- `GET /api/summaries` - Get all summaries
- `GET /api/sources/{id}` - Get specific source
- `GET /api/summaries/{id}` - Get specific summary

## 🤝 Contributing

### Development Workflow
1. **Make changes** to code
2. **Test locally** using development mode
3. **Check logs** for errors
4. **Test API endpoints** manually
5. **Verify database** operations

### Code Structure
- **Frontend:** React with functional components
- **Backend:** Flask with blueprint organization
- **Database:** PostgreSQL with custom ORM layer
- **Validation:** Pydantic models with custom validators

## 📞 Support

### Getting Help
1. **Check logs** in browser console and terminal
2. **Review troubleshooting guide** for common issues
3. **Test individual components** using provided scripts
4. **Verify configuration** files and environment variables

### Common Commands
```bash
# Start everything
python start_application.py

# Initialize database
python database_handler/scripts/init_db.py

# Check database status
python database_handler/scripts/init_db.py --check

# Seed sample data
python database_handler/scripts/seed_data.py

# Test database handler
python example_usage.py
```

---

## 🎉 Success!

Your ASL Summarizer is now fully integrated and ready to use!

- ✅ **Database handler** - Complete PostgreSQL integration
- ✅ **Backend API** - Flask server with all endpoints
- ✅ **Frontend UI** - React application with routing
- ✅ **Authentication** - Development mode bypass
- ✅ **Content processing** - URL and file upload
- ✅ **AI integration** - Claude validation and summarization
- ✅ **Data persistence** - Full CRUD operations

**Next Steps:**
1. Open http://localhost:5173 in your browser
2. Explore the Sources and Summaries pages
3. Try uploading content and generating summaries
4. Review the codebase for customization opportunities

**Happy coding! 🚀**