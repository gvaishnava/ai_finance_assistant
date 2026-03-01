import React, { useState, useEffect, useRef } from 'react';
import { sendMessage, getChatHistory } from '../services/api';
import { TypewriterText, LoadingStatus, ChartRenderer } from './UIComponents';

const ChatInterface = () => {
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
                // Show general questions only in the main chat tab
                const data = await getChatHistory('chat');
                if (data.messages && data.messages.length > 0) {
                    setMessages(data.messages);
                }
            } catch (error) {
                console.error('Error fetching chat history:', error);
            }
        };
        fetchHistory();
    }, []);

    const handleSend = async () => {
        if (!input.trim() || loading) return;

        const userMessage = {
            role: 'user',
            content: input,
            timestamp: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const response = await sendMessage(input, 'chat');

            const assistantMessage = {
                role: 'assistant',
                content: response.response,
                agent: response.agent_display_name,
                citations: response.citations,
                metadata: response.metadata,
                timestamp: new Date().toISOString(),
                isNew: true, // Only this message should animate
            };

            setMessages((prev) => [...prev, assistantMessage]);
        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage = {
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please try again.',
                timestamp: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="flex flex-col h-full bg-gray-50">
            {/* Header */}
            <div className="bg-white border-b border-gray-200 px-6 py-4">
                <h2 className="text-2xl font-bold text-gray-800">AI Finance Assistant</h2>
                <p className="text-sm text-gray-500">Ask me anything about investing and finance</p>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
                {messages.length === 0 && (
                    <div className="text-center py-12">
                        <div className="text-6xl mb-4">💰</div>
                        <h3 className="text-xl font-semibold text-gray-700 mb-2">
                            Welcome to AI Finance Assistant
                        </h3>
                        <p className="text-gray-500 mb-6">
                            I can help you learn about stocks, mutual funds, portfolio analysis, and more!
                        </p>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl mx-auto">
                            {[
                                'What is a mutual fund?',
                                'How do I start investing?',
                                'Explain stock market basics',
                                'What is diversification?',
                            ].map((suggestion, idx) => (
                                <button
                                    key={idx}
                                    onClick={() => setInput(suggestion)}
                                    className="px-4 py-3 bg-white border-2 border-primary-200 rounded-lg hover:border-primary-400 hover:bg-primary-50 transition-all text-left text-sm font-medium text-gray-700"
                                >
                                    {suggestion}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {messages.map((msg, idx) => (
                    <div
                        key={idx}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-slide-in`}
                    >
                        <div className={msg.role === 'user' ? 'message-user' : 'message-assistant'}>
                            {msg.role === 'assistant' && msg.agent && (
                                <div className="text-xs font-semibold mb-1 text-primary-600">
                                    {msg.agent}
                                </div>
                            )}
                            {msg.role === 'assistant' && msg.isNew ? (
                                <TypewriterText
                                    text={msg.content}
                                    delay={5}
                                    onComplete={() => {
                                        // Optional: clear isNew after animation
                                        setMessages(prev => prev.map((m, i) => i === idx ? { ...m, isNew: false } : m));
                                    }}
                                />
                            ) : (
                                <div className="whitespace-pre-wrap">{msg.content}</div>
                            )}
                            {msg.citations && msg.citations.length > 0 && (
                                <div className="mt-2 pt-2 border-t border-gray-200 text-xs text-gray-500">
                                    <div className="font-semibold mb-1">Sources:</div>
                                    {msg.citations.slice(0, 3).map((citation, i) => (
                                        <div key={i}>• {citation.source}</div>
                                    ))}
                                </div>
                            )}
                            {msg.metadata?.visualizations && msg.metadata.visualizations.map((viz, vIdx) => (
                                <ChartRenderer key={vIdx} visualization={viz} />
                            ))}
                        </div>
                    </div>
                ))}

                {loading && (
                    <div className="flex justify-start animate-slide-in">
                        <div className="message-assistant min-w-[200px]">
                            <LoadingStatus />
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="bg-white border-t border-gray-200 px-6 py-4">
                <div className="flex space-x-3">
                    <textarea
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Ask about investing, markets, portfolio analysis..."
                        className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                        rows="2"
                        disabled={loading}
                    />
                    <button
                        onClick={handleSend}
                        disabled={!input.trim() || loading}
                        className="px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-semibold"
                    >
                        Send
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ChatInterface;
