import React, { useState, useRef, useEffect } from 'react';
import { sendMessage, getChatHistory } from '../services/api';
import { TypewriterText, LoadingStatus, ChartRenderer } from './UIComponents';

const TaxAssistant = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const data = await getChatHistory('tax');
                if (data.messages && data.messages.length > 0) {
                    setMessages(data.messages.map(m => ({ ...m, isNew: false })));
                }
            } catch (error) {
                console.error('Error fetching tax history:', error);
            }
        };
        fetchHistory();
    }, []);

    const handleSend = async (overrideInput = null) => {
        const textToSend = overrideInput || input;
        if (!textToSend.trim() || loading) return;

        // Force tax context if not explicit
        const query = textToSend.toLowerCase().includes('tax') ? textToSend : `Tax implication of: ${textToSend}`;

        const userMessage = {
            role: 'user',
            content: textToSend,
            timestamp: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const response = await sendMessage(query, 'tax');

            const assistantMessage = {
                role: 'assistant',
                content: response.response,
                agent: response.agent_display_name,
                citations: response.citations,
                metadata: response.metadata,
                timestamp: new Date().toISOString(),
                isNew: true
            };

            setMessages((prev) => [...prev, assistantMessage]);
        } catch (error) {
            console.error('Error sending message:', error);
            setMessages((prev) => [...prev, {
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please try again.',
                timestamp: new Date().toISOString(),
            }]);
        } finally {
            setLoading(false);
        }
    };

    const suggestions = [
        "How are mutual funds taxed?",
        "Explain Short Term Capital Gains (STCG)",
        "Tax saving options under 80C",
        "How is intraday trading taxed?"
    ];

    return (
        <div className="flex h-full space-x-6 p-6 overflow-hidden bg-gray-50">
            {/* Sidebar / Info */}
            <div className="w-1/3 space-y-4">
                <div className="bg-gradient-to-br from-indigo-600 to-purple-700 rounded-xl p-6 text-white shadow-lg">
                    <div className="flex items-center space-x-3 mb-4">
                        <div className="bg-white/20 p-2 rounded-lg backdrop-blur-sm">
                            <span className="text-2xl">📑</span>
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold">Tax Assistant</h2>
                            <p className="opacity-90 text-xs">AI Powered Educator</p>
                        </div>
                    </div>
                    <p className="opacity-90 text-sm mb-6">Expert guidance on Indian taxation rules for investors. Learn about LTCG, STCG, and more.</p>

                    <div className="space-y-2">
                        <p className="text-xs font-semibold uppercase tracking-wider opacity-75">Quick Topics</p>
                        {suggestions.map((s, idx) => (
                            <button
                                key={idx}
                                onClick={() => handleSend(s)}
                                disabled={loading}
                                className="block w-full text-left px-3 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-sm transition-all hover:translate-x-1"
                            >
                                {s}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 text-sm text-yellow-800 shadow-sm">
                    <div className="flex items-start space-x-2">
                        <span className="text-lg">⚠️</span>
                        <div>
                            <strong>Disclaimer:</strong> This is for educational purposes only. Tax laws are complex. Always consult a Chartered Accountant (CA) for official filing and advice.
                        </div>
                    </div>
                </div>
            </div>

            {/* Chat Area */}
            <div className="flex-1 bg-white rounded-xl shadow-sm border border-gray-200 flex flex-col overflow-hidden">
                <div className="flex-1 overflow-y-auto p-6 space-y-4">
                    {messages.length === 0 && (
                        <div className="h-full flex flex-col items-center justify-center text-gray-400 space-y-4">
                            <div className="w-16 h-16 bg-indigo-50 rounded-full flex items-center justify-center text-3xl">
                                💬
                            </div>
                            <div className="text-center">
                                <p className="font-semibold text-gray-600">Start a Conversation</p>
                                <p className="text-sm">Ask about capital gains, dividends, or exemptions</p>
                            </div>
                        </div>
                    )}

                    {messages.map((msg, idx) => (
                        <div
                            key={idx}
                            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-slide-in`}
                        >
                            <div className={`max-w-[85%] rounded-2xl px-4 py-3 shadow-sm ${msg.role === 'user'
                                ? 'bg-indigo-600 text-white rounded-br-none'
                                : 'bg-white border border-gray-100 text-gray-800 rounded-bl-none'
                                }`}>
                                {msg.role === 'assistant' && msg.agent && (
                                    <div className="text-[10px] font-bold uppercase tracking-wider mb-1 text-indigo-600 opacity-80">
                                        {msg.agent}
                                    </div>
                                )}
                                <div className="space-y-4">
                                    {msg.metadata?.visualizations && msg.metadata.visualizations.map((viz, vIdx) => (
                                        <ChartRenderer key={vIdx} visualization={viz} />
                                    ))}
                                    <div className="whitespace-pre-wrap text-sm">
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
                                {msg.citations && (
                                    <div className="mt-2 pt-2 border-t border-gray-100 text-[10px] opacity-60">
                                        Source: Financial Knowledge Base
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}

                    {loading && (
                        <div className="flex justify-start animate-slide-in">
                            <div className="bg-white border border-gray-100 rounded-2xl rounded-bl-none px-4 py-3 shadow-sm min-w-[200px]">
                                <LoadingStatus />
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                <div className="p-4 border-t border-gray-200 bg-gray-50/50">
                    <div className="flex space-x-3 bg-white p-1 rounded-xl shadow-inner border border-gray-200">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                            placeholder="Ask about taxation logic..."
                            className="flex-1 px-4 py-3 bg-transparent border-none focus:ring-0 text-sm"
                            disabled={loading}
                        />
                        <button
                            onClick={() => handleSend()}
                            disabled={!input.trim() || loading}
                            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-200 disabled:text-gray-500 transition-all font-semibold text-sm shadow-md active:scale-95"
                        >
                            {loading ? 'Thinking...' : 'Analyze'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TaxAssistant;
