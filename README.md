---
title: AI Finance Assistant
emoji: 💰
colorFrom: indigo
colorTo: purple
sdk: docker
pinned: false
---

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

The frontend will be available at ## 🏗️ Architecture

The system uses a **Hierarchical Multi-Agent Orchestration** pattern powered by LangGraph.

### Agentic Workflow
```mermaid
graph TD
    User([User Query]) --> Supervisor{Supervisor Agent}
    Supervisor --> |Keyword/LLM Routing| News[News Agent]
    Supervisor --> |Keyword/LLM Routing| Market[Market Agent]
    Supervisor --> |Keyword/LLM Routing| Portfolio[Portfolio Agent]
    Supervisor --> |Keyword/LLM Routing| Goals[Goal Planning Agent]
    Supervisor --> |Keyword/LLM Routing| Tax[Tax Agent]
    Supervisor --> |Keyword/LLM Routing| QA[Finance Q&A Agent]
    
    subgraph Specialist Agents
        News --> RAG[(FAISS Knowledge Base)]
        Market --> Yahoo[yfinance API]
        Portfolio --> Yahoo
        Goals --> RAG
        QA --> RAG
    end
    
    Specialist Agents --> LLM[Gemini-2.0-Flash / GPT-4o]
    LLM --> Response([Educational Response + Disclaimers])
```

### Key Components

- **LangGraph Orchestration**: Manages the state and transition between agents, allowing for complex multi-turn reasoning.
- **Dynamic Routing**: The Supervisor uses a hybrid approach (Regex keywords + LLM semantic intent) to route queries with high precision and low latency.
- **RAG Tier**: Semantic search over Zerodha Varsity modules using FAISS and OpenAI/Gemini embeddings.
- **Real-time Data Tier**: Integration with `yfinance` for live market snapshots and `Tavily` for external news search.

## 🛡️ Reliability & Quality Assurance

To ensure a production-ready experience, the project implements several reliability patterns:

- **Retry Mechanisms**: Exponential backoff for LLM API calls to handle rate limits and transient errors.
- **Fallback Models**: Automatic fallback to a secondary LLM (e.g., from OpenAI to Gemini) if the primary provider is unavailable.
- **Self-Correction (Ticker Resolver)**: The Ticker Resolver agent uses search and LLM validation to fix ambiguous company names (e.g., "Reliance" -> `RELIANCE.NS`).
- **Input Validation**: Strict Pydantic models for all API interactions to ensure data integrity.

## 🧪 Testing & Coverage

The project maintains a rigorous testing standard with **80%+ code coverage**.

- **Total Tests**: 70+ passing test cases.
- **Suite Types**:
  - **Unit Tests**: Per-agent logic, utility functions, and model parsing.
  - **Integration Tests**: End-to-end API flows and LangGraph state transitions.
  - **RAG Tests**: Knowledge base indexing and retrieval accuracy.
- **Coverage Report**:
  - `agents`: ~90%
  - `workflow/supervisor`: 80%
  - `data/portfolio`: 94%
  - `core`: 78%

```bash
# Run coverage
pytest --cov=src --cov-report=term-missing tests/
```

## 📋 Prerequisites & Setup

- **Python**: 3.10+
- **APIs Required**:
  - `OPENAI_API_KEY` (Primary LLM & Embeddings)
  - `GEMINI_API_KEY` (Fallback LLM)
  - `TAVILY_API_KEY` (News search)
  - `LANGCHAIN_API_KEY` (Optional tracing)

### Installation
```bash
python -m venv venv
./venv/Scripts/activate
pip install -r requirements.txt
python scripts/init_knowledge_base.py
python main.py
```

## 📚 Knowledge Base
The RAG system is indexed with **14 modules of Zerodha Varsity**, covering everything from "Introduction to Stock Markets" to "Personal Finance" and "Risk Management".

## 🔒 Regulatory Compliance
Automated disclaimer injection ensures all advice is framed as **educational content**, adhering to financial information regulations.

## 🛠️ Troubleshooting & Restarting

### How to Restart the Application
If the application becomes unresponsive or "restarts" automatically when you try to close it, follow these steps:

1.  **Check for "QuickEdit" Mode**: If the terminal says "Select" in the title bar, press **Enter** to unfreeze it before `Ctrl+C`.
2.  **The "Nuke" Option (Stop Everything)**:
    If `Ctrl+C` fails or the app keeps restarting, you can force-kill all instances of Python and Node. **Warning**: This will close ALL your running Python and Node programs.
    ```powershell
    # Kill all Python processes (Backend)
    taskkill /F /IM python.exe
    
    # Kill all Node processes (Frontend)
    taskkill /F /IM node.exe
    ```
3.  **Specific Port Kill (Safer)**:
    If you only want to kill the processes using the app's ports:
    - **Backend (8000)**: `netstat -ano | findstr :8000` then `taskkill /F /PID <PID>`
    - **Frontend (5173)**: `netstat -ano | findstr :5173` then `taskkill /F /PID <PID>`
4.  **Disable Auto-Reload**:
    If the app restarts whenever you save a file or press `Ctrl+C`, set `debug: false` in `config.yaml` to disable the `uvicorn` file watcher.

### Common Issues
- **Port 8000 already in use**: Use the "Nuke" or "Port Kill" commands above.
- **Vector Store indexing**: This is normal on first run.

## 📞 Support
For support, contact the development team or check the documentation.

---
**Version**: 1.1.0  |  **Coverage**: 80%  |  **Last Updated**: March 2026

