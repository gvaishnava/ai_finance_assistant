# AI Finance Assistant - Quick Start Guide

This guide will help you get the AI Finance Assistant up and running quickly.

## Prerequisites

- Python 3.10+
- Node.js 16+
- Google Gemini API key

## Step-by-Step Setup

### 1. Backend Setup

```bash
# Navigate to project directory
cd "e:\project\genai\financial ai chatbot"

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
copy .env.example .env
# Edit .env and add your Gemini API key:
# GEMINI_API_KEY=your_api_key_here
```

### 2. Initialize Knowledge Base

```bash
# This processes all Zerodha PDFs and creates the vector store
# Takes 5-10 minutes on first run
python scripts\init_knowledge_base.py
```

### 3. Start Backend Server

```bash
python main.py
```

Backend will be available at: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

### 4. Frontend Setup (New Terminal)

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:3000`

## What You'll See

### Backend Terminal:
```
INFO:     Initializing AI Finance Assistant...
INFO:     Loading knowledge base...
INFO:     Loaded vector store with 1234 documents
INFO:     Initialization complete!
INFO:     Starting server on 0.0.0.0:8000
INFO:     Application startup complete.
```

### Frontend Terminal:
```
VITE v5.0.0  ready in 1234 ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

## Testing the System

### 1. Open Browser
Navigate to `http://localhost:3000`

### 2. Try the Chat
- Click on "Chat" tab
- Ask: "What is a mutual fund?"
- You should get an educational response from the Finance Q&A Agent

### 3. Test Market Data
- Click on "Market" tab
- View market indices (NIFTY, SENSEX)
- Search for a stock: "RELIANCE.NS"

### 4. Analyze Portfolio
- Click on "Portfolio" tab
- Add holdings:
  - Symbol: RELIANCE.NS, Quantity: 10
  - Symbol: TCS.NS, Quantity: 5
- Click "Analyze Portfolio"

### 5. Set Profile
- Click on "Profile" tab
- Set your knowledge level and risk tolerance
- Save changes

## Features to Explore

### Multi-Agent System
The system will automatically route your questions to the right agent:
- **General questions** → Finance Q&A Agent  
- **Portfolio questions** → Portfolio Agent
- **Market questions** → Market Agent
- **Goal questions** → Goal Planning Agent
- **News questions** → News Agent
- **Tax questions** → Tax Agent

### Real-Time Market Data
- Live quotes from NSE/BSE
- Market indices updated every minute
- Historical data available

### RAG-Enhanced Responses
- All responses backed by Zerodha course materials
- Citations shown for educational content
- 14 modules of financial knowledge

## Troubleshooting

**Backend won't start:**
- Check if port 8000 is available
- Verify GEMINI_API_KEY is set in .env file
- Ensure all dependencies are installed

**Frontend won't start:**
- Check if port 3000 is available
- Run `npm install` again if packages are missing
- Clear node_modules and reinstall

**Knowledge base loading fails:**
- Verify Zerodha PDFs are in `zerodha_course_on_stockmarket/` folder
- Check API key has sufficient quota
- See logs in `logs/app.log`

**Market data not working:**
- Ensure internet connection is active
- Use correct symbol format (e.g., RELIANCE.NS for NSE)
- Check yfinance service status

## Next Steps

Once everything is working:
1. Experiment with different types of questions
2. Try portfolio analysis with real holdings
3. Explore the different agent responses
4. Review the API documentation at `/docs`

## Need Help?

- Check logs in `logs/app.log`
- Review API docs at `http://localhost:8000/docs`
- See README.md for detailed documentation

---

**Happy Learning! 📚💰**
