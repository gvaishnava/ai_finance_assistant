# React Frontend - AI Financial Assistant

This is the modern, responsive React frontend for the AI Finance Assistant. It provides a seamless interface for interacting with the multi-agent financial planning system.

## 🚀 Features

- **💬 Intelligent Chat Interface**: Real-time interaction with specialized agents (Market, News, Tax, etc.) with automatic message streaming.
- **📊 Market Dashboard**: Comprehensive stock and index tracking using `yfinance` data, featuring interactive price charts and sector comparisons.
- **🎯 Goal Planner**: Advanced financial goal tracking with AI-driven progress analysis and milestone planning.
- **💼 Portfolio View**: Dynamic allocation analysis and real-time value tracking of user holdings.
- **🧠 Ticker Resolution**: Integrated company search that resolves natural language names to exact market symbols.

## 🛠️ Tech Stack

- **Framework**: [React 18](https://react.dev/)
- **Build Tool**: [Vite](https://vitejs.dev/)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/) for a modern, responsive design.
- **State Management**: React Hooks (useState, useEffect) for lightweight, efficient state.
- **Data Visualization**: [Recharts](https://recharts.org/) for beautiful, responsive financial charts.
- **API Client**: [Axios](https://axios-http.com/) for typed backend communication.

## 📦 Components

- `ChatInterface.jsx`: Main conversational window with message bubbles and agent status.
- `MarketDashboard.jsx`: Stock search, indices tracking, and quote visualization.
- `GoalPlanner.jsx`: Interface for creating goals and viewing AI-generated planning history.
- `PortfolioView.jsx`: Visual representation of assets and diversification.
- `UIComponents.jsx`: Reusable design tokens (Typewriter effect, Loaders, Charts).

## 🔨 Setup & Deployment

### Prerequisites
- Node.js 16+
- npm or yarn

### Installation
```bash
npm install
```

### Development
```bash
npm run dev
```

### Production Build
```bash
npm run build
```

The frontend will be available at `http://localhost:5173` by default (Vite standard).
