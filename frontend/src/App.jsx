import React, { useState } from 'react';
import ChatInterface from './components/ChatInterface';
import MarketDashboard from './components/MarketDashboard';
import PortfolioView from './components/PortfolioView';
import UserProfile from './components/UserProfile';
import NewsDashboard from './components/NewsDashboard';
import TaxAssistant from './components/TaxAssistant';
import GoalPlanner from './components/GoalPlanner';

function App() {
    const [activeTab, setActiveTab] = useState('chat');

    const tabs = [
        { id: 'chat', label: 'Chat', icon: '💬', component: ChatInterface },
        { id: 'market', label: 'Market', icon: '📊', component: MarketDashboard },
        { id: 'news', label: 'News', icon: '📰', component: NewsDashboard },
        { id: 'portfolio', label: 'Portfolio', icon: '💼', component: PortfolioView },
        { id: 'goals', label: 'Goals', icon: '🎯', component: GoalPlanner },
        { id: 'tax', label: 'Tax', icon: '📑', component: TaxAssistant },
        { id: 'profile', label: 'Profile', icon: '👤', component: UserProfile },
    ];

    const ActiveComponent = tabs.find(tab => tab.id === activeTab)?.component;

    return (
        <div className="h-screen flex flex-col bg-gray-50">
            {/* Header */}
            <header className="bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg">
                <div className="container mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
                                <span className="text-2xl">💰</span>
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold">AI Finance Assistant</h1>
                                <p className="text-xs text-primary-100">Powered by Google Gemini & LangGraph</p>
                            </div>
                        </div>
                        <div className="flex items-center space-x-4">
                            <div className="text-right">
                                <p className="text-sm font-semibold">Multi-Agent System</p>
                                <p className="text-xs text-primary-100">6 Specialized Agents</p>
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            {/* Navigation */}
            <nav className="bg-white border-b border-gray-200 shadow-sm">
                <div className="container mx-auto px-6">
                    <div className="flex space-x-1">
                        {tabs.map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`px-6 py-4 font-semibold transition-all relative ${activeTab === tab.id
                                    ? 'text-primary-600 border-b-2 border-primary-600'
                                    : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
                                    }`}
                            >
                                <span className="mr-2">{tab.icon}</span>
                                {tab.label}
                            </button>
                        ))}
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main className="flex-1 overflow-hidden">
                <div className="container mx-auto h-full">
                    {ActiveComponent && <ActiveComponent />}
                </div>
            </main>

            {/* Footer */}
            <footer className="bg-white border-t border-gray-200 py-3">
                <div className="container mx-auto px-6">
                    <div className="flex justify-between items-center text-sm text-gray-500">
                        <p>© 2026 AI Finance Assistant - Educational Purposes Only</p>
                        <div className="flex items-center space-x-4">
                            <span>✓ RAG-Enhanced</span>
                            <span>✓ Real-time Data</span>
                            <span>✓ Regulatory Compliant</span>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    );
}

export default App;
