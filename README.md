# AI Finance Assistant

An intelligent multi-agent financial education system powered by Google Gemini, LangGraph, and RAG (Retrieval-Augmented Generation). This system helps users learn about investing through personalized, accessible financial education.

## 🌟 Features

### Multi-Agent System
- **Finance Q&A Agent** - Handles general financial education queries with knowledge-level adaptation
- **Portfolio Analysis Agent** - Reviews portfolios and provides diversification insights
- **Market Analysis Agent** - Delivers real-time market insights using yfinance
- **Goal Planning Agent** - Assists with financial goal setting and tracking
- **News Synthesizer Agent** - Summarizes and contextualizes financial news
- **Tax Education Agent** - Explains tax concepts (educational only)
- **Ticker Resolver Agent** - Intelligently resolves company names to exact stock tickers using LLM + Search

### Core Capabilities
- 🔍 **RAG-Enhanced** - Uses FAISS vector database with Zerodha course materials (14 modules)
- 🤖 **LangGraph Orchestration** - Intelligent routing between specialized agents
- 📊 **Real-Time Market Data** - Live stock quotes and indices via yfinance
- 💼 **Portfolio Tracking** - Analyze holdings, allocation, and performance
- 🎯 **Goal Management** - Track progress toward financial objectives
- ⚠️ **Regulatory Compliance** - Automatic disclaimers for educational content

## 📋 Prerequisites

- Python 3.10 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- Node.js 16+ (for React frontend)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd "e:\project\genai\financial ai chatbot"

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key

```bash
# Copy the example environment file
copy .env.example .env

# Edit .env and add your API keys
# GEMINI_API_KEY=your_gemini_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here
# TAVILY_API_KEY=your_tavily_api_key_here
```

### 3. Initialize Knowledge Base

```bash
# This processes the Zerodha course PDFs and creates the vector store
# It may take several minutes on first run
python scripts\init_knowledge_base.py
```

### 4. Start the Backend

```bash
python main.py
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### 5. Start the Frontend

In a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 🏗️ Architecture

```
User Query → Supervisor Agent → Specialized Agent → RAG Retrieval → LLM (Gemini) → Response
```

### Components

- **LangGraph Workflow** - Orchestrates multi-agent conversations
- **Supervisor Agent** - Routes queries using keyword + LLM-based routing
- **Specialized Agents** - Domain-specific processing with RAG integration
- **FAISS Vector Store** - Semantic search over financial education content
- **Google Gemini** - LLM for response generation and embeddings
- **yfinance** - Real-time market data integration
- **FastAPI** - REST API for frontend integration

## 📁 Project Structure

```
├── src/
│   ├── agents/         # 6 specialized agents + base agent
│   ├── core/           # LLM client, session, disclaimers
│   ├── data/           # Market data, portfolio, user profile
│   ├── rag/            # Vector store, embeddings, retriever
│   ├── web_app/        # FastAPI application & routes
│   ├── utils/          # Logging, formatting, validation
│   └── workflow/       # LangGraph state & orchestration
├── zerodha_course_on_stockmarket/  # Knowledge base (14 modules)
├── scripts/            # Utility scripts
├── tests/              # Unit and integration tests
├── config.yaml         # Application configuration
├── main.py             # Application entry point
└── requirements.txt    # Python dependencies
```

## 🔌 API Endpoints

### Chat
- `POST /api/chat` - General chat with automatic agent routing
- `POST /api/chat/portfolio` - Portfolio-specific analysis
- `POST /api/chat/goal` - Goal planning assistance
- `GET /api/chat/history/{session_id}` - Conversation history

### Market
- `GET /api/market/quote/{symbol}` - Stock quote (e.g., RELIANCE.NS)
- `GET /api/market/trends` - Market indices (NIFTY, SENSEX)
- `GET /api/market/search/{query}` - Symbol search

### User
- `GET /api/user/profile/{session_id}` - User profile
- `PUT /api/user/profile/{session_id}` - Update preferences

### Health
- `GET /health` - System health check

## 💡 Usage Examples

### Python Client Example

```python
import requests

# Chat
response = requests.post("http://localhost:8000/api/chat", json={
    "message": "What is a mutual fund?",
    "session_id": "abc123"
})
print(response.json()['response'])

# Portfolio Analysis
response = requests.post("http://localhost:8000/api/chat/portfolio", json={
    "holdings": [
        {"symbol": "RELIANCE.NS", "quantity": 10},
        {"symbol": "TCS.NS", "quantity": 5}
    ],
    "message": "Analyze my portfolio"
})

# Market Data
quote = requests.get("http://localhost:8000/api/market/quote/RELIANCE.NS")
print(quote.json())
```

## ⚙️ Configuration

Edit `config.yaml` to customize:

- Agent system prompts and behavior
- RAG parameters (chunk size, top-k retrieval)
- Market data caching
- Session management
- Disclaimers

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_agents.py

# Run with coverage
pytest --cov=src tests/
```

## 📚 Knowledge Base

The system uses Zerodha's comprehensive course materials:
- Module 1: Introduction to Stock Markets
- Module 2: Technical Analysis
- Module 3: Fundamental Analysis
- Module 4-6: Futures & Options
- Module 7: Markets & Taxation
- Module 8: Currency & Commodity
- Module 9: Risk Management
- Module 10-14: Trading Systems, Personal Finance, etc.

## 🔒 Regulatory Compliance

All responses include appropriate disclaimers:
- General financial education disclaimer
- Tax advice disclaimer (recommends professional consultation)
- Portfolio analysis disclaimer (not investment advice)

## 🤝 Contributing

This is a private project. For questions or issues, contact the development team.

## � License

Proprietary - Internal Use Only

## 🆘 Troubleshooting

**Issue**: Knowledge base fails to load
- Check that Zerodha PDFs are in `zerodha_course_on_stockmarket/`
- Verify GEMINI_API_KEY is set
- Check logs in `logs/app.log`

**Issue**: Market data not available
- yfinance requires internet connection
- Some symbols may need .NS or .BO suffix for Indian stocks
- Check symbol format: `RELIANCE.NS` (NSE) or `RELIANCE.BO` (BSE)

**Issue**: API key errors
- Ensure `.env` file exists with `GEMINI_API_KEY`
- Verify API key is active at https://makersuite.google.com

## 📞 Support

For support, contact the development team or check the documentation.

---

**Version**: 1.0.0  
**Last Updated**: January 2026
