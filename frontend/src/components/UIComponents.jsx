import React, { useState, useEffect } from 'react';
import {
    PieChart, Pie, Cell, ResponsiveContainer,
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
    LineChart, Line
} from 'recharts';

const CHART_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

export const TypewriterText = ({ text, delay = 10, onComplete }) => {
    const [displayedText, setDisplayedText] = useState('');
    const [currentIndex, setCurrentIndex] = useState(0);

    useEffect(() => {
        if (!text) return;
        if (currentIndex < text.length) {
            const timeout = setTimeout(() => {
                setDisplayedText(prev => prev + text[currentIndex]);
                setCurrentIndex(prev => prev + 1);
            }, delay);
            return () => clearTimeout(timeout);
        } else if (onComplete) {
            onComplete();
        }
    }, [currentIndex, delay, text, onComplete]);

    return <div className="whitespace-pre-wrap">{displayedText}</div>;
};

export const LoadingStatus = () => {
    const [messageIndex, setMessageIndex] = useState(0);
    const messages = [
        "Analyzing your query...",
        "Orchestrating financial agents...",
        "Consulting knowledge base...",
        "Synthesizing educational response...",
        "Finalizing analysis..."
    ];

    useEffect(() => {
        const interval = setInterval(() => {
            setMessageIndex((prev) => (prev + 1) % messages.length);
        }, 3000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="flex flex-col space-y-2">
            <div className="flex space-x-2 items-center">
                <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
            <div className="text-xs text-gray-500 font-medium italic animate-pulse">
                {messages[messageIndex]}
            </div>
        </div>
    );
};

export const ChartRenderer = ({ visualization }) => {
    if (!visualization || !visualization.data) return null;

    const renderChart = () => {
        switch (visualization.type) {
            case 'pie':
                return (
                    <PieChart>
                        <Pie
                            data={visualization.data}
                            innerRadius={visualization.innerRadius || 0}
                            outerRadius={visualization.outerRadius || 80}
                            paddingAngle={5}
                            dataKey="value"
                        >
                            {visualization.data.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.fill || CHART_COLORS[index % CHART_COLORS.length]} />
                            ))}
                        </Pie>
                        <Tooltip formatter={(value) => `${value}`} />
                        <Legend />
                    </PieChart>
                );
            case 'bar':
                return (
                    <BarChart data={visualization.data}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="value" fill="#3b82f6" />
                    </BarChart>
                );
            case 'line':
                return (
                    <LineChart data={visualization.data}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey={visualization.xAxis || "date"} />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey={visualization.yAxis || "price"} stroke="#3b82f6" activeDot={{ r: 8 }} />
                    </LineChart>
                );
            default:
                return <p className="text-xs text-gray-400">Unsupported chart type: {visualization.type}</p>;
        }
    };

    return (
        <div className="mt-6 p-6 bg-white rounded-2xl border border-gray-200 shadow-md animate-fade-in flex flex-col" style={{ height: '400px', minHeight: '400px', width: '100%', minWidth: '300px', overflow: 'visible' }}>
            <h4 className="text-base font-bold text-gray-800 mb-4 border-b border-gray-100 pb-2">{visualization.title || 'Data Visualization'}</h4>
            <div className="flex-1 w-full" style={{ minHeight: '300px' }}>
                <ResponsiveContainer width="99%" height="99%">
                    {renderChart()}
                </ResponsiveContainer>
            </div>
        </div>
    );
};
