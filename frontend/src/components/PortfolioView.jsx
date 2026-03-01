import React, { useState, useEffect, useRef } from 'react';
import { sendPortfolioMessage, getFullSession, getChatHistory } from '../services/api';
import { LoadingStatus, TypewriterText, ChartRenderer } from './UIComponents';

const PortfolioView = () => {
    const [holdings, setHoldings] = useState([{ symbol: '', quantity: '', average_price: '' }]);
    const [messages, setMessages] = useState([]);
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [initialLoading, setInitialLoading] = useState(true);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        if (messages.length > 0) {
            scrollToBottom();
        }
    }, [messages, analysis]);

    useEffect(() => {
        const fetchSavedPortfolio = async () => {
            try {
                const data = await getFullSession();
                if (data.portfolio && data.portfolio.holdings && data.portfolio.holdings.length > 0) {
                    setHoldings(data.portfolio.holdings);
                }

                const historyData = await getChatHistory('portfolio');
                if (historyData.messages && historyData.messages.length > 0) {
                    setMessages(historyData.messages);
                }
            } catch (error) {
                console.error('Error fetching saved portfolio:', error);
            } finally {
                setInitialLoading(false);
            }
        };
        fetchSavedPortfolio();
    }, []);

    const addHolding = () => {
        setHoldings([...holdings, { symbol: '', quantity: '', average_price: '' }]);
    };

    const removeHolding = (index) => {
        setHoldings(holdings.filter((_, i) => i !== index));
    };

    const updateHolding = (index, field, value) => {
        const updated = [...holdings];
        updated[index][field] = value;
        setHoldings(updated);
    };

    const analyzePortfolio = async () => {
        const validHoldings = holdings.filter(h => h.symbol && h.quantity);
        if (validHoldings.length === 0) return;

        setLoading(true);
        try {
            const response = await sendPortfolioMessage(
                validHoldings.map(h => ({
                    symbol: h.symbol,
                    quantity: parseFloat(h.quantity),
                    average_price: h.average_price ? parseFloat(h.average_price) : null
                }))
            );
            const assistantMsg = {
                role: 'assistant',
                content: response.response,
                agent: response.agent_display_name,
                metadata: response.metadata,
                isNew: true
            };
            setAnalysis(assistantMsg);
            setMessages(prev => [...prev, assistantMsg]);
        } catch (error) {
            console.error('Error analyzing portfolio:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-6 space-y-6 h-full overflow-y-auto custom-scrollbar">
            <div>
                <h2 className="text-2xl font-bold text-gray-800 mb-1">Portfolio Analysis</h2>
                <p className="text-sm text-gray-500">Add your holdings for educational analysis</p>
            </div>

            {/* Holdings Input */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Your Holdings</h3>

                <div className="space-y-3">
                    {initialLoading ? (
                        <div className="flex justify-center py-8">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
                        </div>
                    ) : (
                        holdings.map((holding, index) => (
                            <div key={index} className="flex space-x-3">
                                <input
                                    type="text"
                                    placeholder="Symbol (e.g., RELIANCE.NS)"
                                    value={holding.symbol}
                                    onChange={(e) => updateHolding(index, 'symbol', e.target.value.toUpperCase())}
                                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                                />
                                <input
                                    type="number"
                                    placeholder="Quantity"
                                    value={holding.quantity}
                                    onChange={(e) => updateHolding(index, 'quantity', e.target.value)}
                                    className="w-32 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                                />
                                <input
                                    type="number"
                                    placeholder="Avg. Price"
                                    value={holding.average_price || ''}
                                    onChange={(e) => updateHolding(index, 'average_price', e.target.value)}
                                    className="w-32 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                                />
                                {holdings.length > 1 && (
                                    <button
                                        onClick={() => removeHolding(index)}
                                        className="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                    >
                                        Remove
                                    </button>
                                )}
                            </div>
                        ))
                    )}
                </div>

                <div className="flex justify-between mt-4">
                    <button
                        onClick={addHolding}
                        className="px-4 py-2 text-primary-600 hover:bg-primary-50 rounded-lg transition-colors font-semibold"
                    >
                        + Add Holding
                    </button>
                    <button
                        onClick={analyzePortfolio}
                        disabled={loading || holdings.every(h => !h.symbol)}
                        className="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:bg-gray-300 transition-colors font-semibold"
                    >
                        {loading ? 'Analyzing...' : 'Analyze Portfolio'}
                    </button>
                </div>
            </div>

            {/* Analysis Results History */}
            {messages.length > 0 && (
                <div className="space-y-4">
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-slide-in`}>
                            <div className={`max-w-[90%] rounded-xl p-4 ${msg.role === 'user'
                                ? 'bg-primary-50 border border-primary-100 text-primary-900'
                                : 'bg-white border border-gray-200 text-gray-800'}`}>
                                {msg.role === 'assistant' && (
                                    <div className="text-xs font-semibold text-primary-600 mb-1">
                                        {msg.agent || 'Portfolio Agent'}
                                    </div>
                                )}
                                <div className="space-y-4">
                                    {msg.metadata?.visualizations && msg.metadata.visualizations.map((viz, vIdx) => (
                                        <ChartRenderer key={vIdx} visualization={viz} />
                                    ))}
                                    <div className="whitespace-pre-wrap leading-relaxed overflow-x-auto text-sm">
                                        {msg.role === 'assistant' && msg.isNew ? (
                                            <TypewriterText
                                                text={msg.content}
                                                delay={5}
                                                onComplete={() => {
                                                    setMessages(prev => prev.map((m, i) => i === idx ? { ...m, isNew: false } : m));
                                                }}
                                            />
                                        ) : (
                                            msg.content
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}


            {/* Tips */}
            <div className="bg-green-50 border border-green-200 rounded-xl p-4">
                <div className="flex items-start space-x-3">
                    <div className="text-2xl">💡</div>
                    <div>
                        <h4 className="font-semibold text-green-900 mb-1">Portfolio Tips</h4>
                        <p className="text-sm text-green-700">
                            • This analysis is educational only, not investment advice
                            <br />
                            • Use Indian stock symbols with .NS (NSE) or .BO (BSE)
                            <br />
                            • The AI will help you understand diversification concepts
                        </p>
                    </div>
                </div>
            </div>

            <div ref={messagesEndRef} />
        </div>
    );
};

export default PortfolioView;
