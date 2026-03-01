import React, { useState, useEffect } from 'react';
import { getMarketTrends, getStockQuote, getChatHistory, sendMessage } from '../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { TypewriterText, LoadingStatus, ChartRenderer } from './UIComponents';

const MarketDashboard = () => {
    const [indices, setIndices] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchSymbol, setSearchSymbol] = useState('');
    const [searchedStock, setSearchedStock] = useState(null);
    const [searchLoading, setSearchLoading] = useState(false);
    const [history, setHistory] = useState([]);
    const [analysisLoading, setAnalysisLoading] = useState(false);
    const [currentAnalysis, setCurrentAnalysis] = useState(null);

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const data = await getChatHistory('market');
                if (data.messages && data.messages.length > 0) {
                    setHistory(data.messages.map(m => ({ ...m, isNew: false })));
                    // Show most recent analysis if available
                    const lastAssistantMsg = [...data.messages].reverse().find(m => m.role === 'assistant');
                    if (lastAssistantMsg) {
                        setCurrentAnalysis({
                            content: lastAssistantMsg.content,
                            metadata: lastAssistantMsg.metadata,
                            isNew: false
                        });
                    }
                }
            } catch (error) {
                console.error('Error fetching market history:', error);
            }
        };
        fetchHistory();
    }, []);

    useEffect(() => {
        fetchMarketData();
        const interval = setInterval(fetchMarketData, 60000); // Refresh every minute
        return () => clearInterval(interval);
    }, []);

    const fetchMarketData = async () => {
        try {
            const data = await getMarketTrends();
            setIndices(data.indices);
        } catch (error) {
            console.error('Error fetching market data:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = async () => {
        if (!searchSymbol.trim()) return;

        setSearchLoading(true);
        try {
            const stock = await getStockQuote(searchSymbol);
            setSearchedStock(stock);
        } catch (error) {
            console.error('Error searching stock:', error);
            setSearchedStock({ error: 'Stock not found' });
        } finally {
            setSearchLoading(false);
        }
    };

    const analyzeStock = async (stock) => {
        setAnalysisLoading(true);
        setCurrentAnalysis(null);
        try {
            const prompt = `Provide a market analysis and perspective for ${stock.name} (${stock.symbol}) currently trading at ${stock.price} ${stock.currency}`;
            const response = await sendMessage(prompt, 'market', { stock_name: stock.name, stock_symbol: stock.symbol });
            const assistantMsg = {
                role: 'assistant',
                content: response.response,
                metadata: response.metadata,
                isNew: true
            };
            setCurrentAnalysis(assistantMsg);
            setHistory(prev => [...prev,
            { role: 'user', content: prompt, metadata: { stock_name: stock.name, stock_symbol: stock.symbol } },
                assistantMsg
            ]);
        } catch (error) {
            console.error('Error analyzing stock:', error);
        } finally {
            setAnalysisLoading(false);
        }
    };

    const formatCurrency = (value, currency = 'INR') => {
        if (!value) return 'N/A';
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value);
    };

    const formatPercentage = (value) => {
        if (!value) return 'N/A';
        const sign = value > 0 ? '+' : '';
        return `${sign}${value.toFixed(2)}%`;
    };

    const renderIndexCard = (index) => {
        const isPositive = index.change_percent > 0;

        return (
            <div key={index.symbol} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-2">
                    <h3 className="text-lg font-semibold text-gray-800">{index.name}</h3>
                    <span className="text-xs font-medium text-gray-500">{index.symbol}</span>
                </div>
                <div className="flex items-baseline space-x-2 mb-2">
                    <span className="text-3xl font-bold text-gray-900">{formatCurrency(index.price, index.currency)}</span>
                </div>
                <div className={`flex items-center space-x-2 ${isPositive ? 'text-success-600' : 'text-danger-600'}`}>
                    <span className="text-lg font-semibold">
                        {formatPercentage(index.change_percent)}
                    </span>
                    <span className="text-sm">
                        {isPositive ? '↑' : '↓'} {formatCurrency(Math.abs(index.change || 0), index.currency)}
                    </span>
                </div>
            </div>
        );
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
                    <p className="text-gray-500">Loading market data...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="p-6 space-y-6 h-full overflow-y-auto custom-scrollbar">
            {/* Header */}
            <div>
                <h2 className="text-2xl font-bold text-gray-800 mb-1">Market Overview</h2>
                <p className="text-sm text-gray-500">Real-time market data powered by yfinance</p>
            </div>

            {/* Stock Search */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Search Stock</h3>
                <div className="flex space-x-3">
                    <input
                        type="text"
                        value={searchSymbol}
                        onChange={(e) => setSearchSymbol(e.target.value.toUpperCase())}
                        onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                        placeholder="Enter symbol (e.g., RELIANCE.NS)"
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                    <button
                        onClick={handleSearch}
                        disabled={searchLoading}
                        className="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:bg-gray-300 transition-colors font-semibold"
                    >
                        {searchLoading ? 'Searching...' : 'Search'}
                    </button>
                </div>

                {searchedStock && !searchedStock.error && (
                    <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <p className="text-sm text-gray-500">Name</p>
                                <p className="font-semibold text-gray-800">{searchedStock.name}</p>
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">Price</p>
                                <p className="font-semibold text-gray-800">{formatCurrency(searchedStock.price, searchedStock.currency)}</p>
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">Change</p>
                                <p className={`font-semibold ${searchedStock.change_percent > 0 ? 'text-success-600' : 'text-danger-600'}`}>
                                    {formatPercentage(searchedStock.change_percent)}
                                </p>
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">Sector</p>
                                <p className="font-semibold text-gray-800">{searchedStock.sector || 'N/A'}</p>
                            </div>
                        </div>
                        <button
                            onClick={() => analyzeStock(searchedStock)}
                            disabled={analysisLoading}
                            className="mt-4 w-full py-2 bg-indigo-50 text-indigo-700 rounded-lg hover:bg-indigo-100 font-bold text-sm transition-all flex items-center justify-center space-x-2"
                        >
                            {analysisLoading ? <div className="w-4 h-4 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div> : '⚡ Get AI Perspective'}
                        </button>
                    </div>
                )}

                {searchedStock && searchedStock.error && (
                    <div className="mt-4 p-4 bg-red-50 text-red-600 rounded-lg">
                        {searchedStock.error}
                    </div>
                )}
            </div>

            {/* Market Indices */}
            <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Major Indices</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {indices.map(renderIndexCard)}
                </div>
            </div>
            {/* Analysis History Display */}
            {(currentAnalysis || analysisLoading) && (
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden animate-slide-in">
                    <div className="bg-indigo-600 px-6 py-3 text-white flex justify-between items-center">
                        <h3 className="font-bold flex items-center"><span className="mr-2">📈</span> Market Analysis</h3>
                        <div className="text-[10px] bg-white/20 px-2 py-0.5 rounded uppercase font-bold tracking-widest">Powered by Market Agent</div>
                    </div>
                    <div className="p-6">
                        {analysisLoading ? (
                            <LoadingStatus />
                        ) : (
                            <div className="space-y-4">
                                {currentAnalysis?.metadata?.visualizations && currentAnalysis.metadata.visualizations.map((viz, vIdx) => (
                                    <ChartRenderer key={vIdx} visualization={viz} />
                                ))}
                                <div className="prose prose-sm max-w-none text-gray-700">
                                    {currentAnalysis?.isNew ? (
                                        <TypewriterText
                                            text={currentAnalysis.content}
                                            delay={3}
                                            onComplete={() => setCurrentAnalysis(prev => ({ ...prev, isNew: false }))}
                                        />
                                    ) : (
                                        <div className="whitespace-pre-wrap">{currentAnalysis?.content}</div>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Past Analyses Gallery */}
            {history.length > 0 && (
                <div>
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Past Market Insights</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {history.filter(m => m.role === 'assistant').slice(-4).reverse().map((m, i) => {
                            const msgIdx = history.indexOf(m);
                            const userMsg = msgIdx > 0 ? history[msgIdx - 1] : null;
                            const stockSymbol = userMsg?.metadata?.stock_symbol;

                            return (
                                <div key={i} className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-all cursor-pointer" onClick={() => setCurrentAnalysis({ ...m, isNew: false })}>
                                    <div className="flex justify-between items-start mb-2">
                                        <p className="text-xs text-gray-400">{new Date(m.timestamp).toLocaleDateString()}</p>
                                        {stockSymbol && <span className="bg-indigo-100 text-indigo-700 text-[8px] font-bold px-1.5 py-0.5 rounded">{stockSymbol}</span>}
                                    </div>
                                    <p className="text-sm text-gray-700 line-clamp-2">{m.content.substring(0, 150)}...</p>
                                    <div className="mt-2 text-[10px] font-bold text-indigo-500 uppercase">View Report →</div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
};

export default MarketDashboard;
