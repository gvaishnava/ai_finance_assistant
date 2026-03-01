import React, { useState } from 'react';
import { sendMessage, getChatHistory } from '../services/api';
import api from '../services/api';
import { TypewriterText, LoadingStatus, ChartRenderer } from './UIComponents';

const NewsDashboard = () => {
    const [query, setQuery] = useState('');
    const [articles, setArticles] = useState([]);
    const [loading, setLoading] = useState(false);
    const [analyzing, setAnalyzing] = useState(null); // URL of article being analyzed
    const [analysis, setAnalysis] = useState(null);
    const [history, setHistory] = useState([]);

    React.useEffect(() => {
        const fetchHistory = async () => {
            try {
                const data = await getChatHistory('news');
                if (data.messages && data.messages.length > 0) {
                    setHistory(data.messages.map(m => ({ ...m, isNew: false })));
                    // Show most recent analysis if available
                    const lastAssistantMsg = [...data.messages].reverse().find(m => m.role === 'assistant');
                    if (lastAssistantMsg) {
                        const msgIdx = data.messages.indexOf(lastAssistantMsg);
                        const userMsg = msgIdx > 0 ? data.messages[msgIdx - 1] : null;
                        const title = userMsg?.metadata?.article_title;

                        setAnalysis({
                            content: lastAssistantMsg.content,
                            article: title ? { title } : null,
                            metadata: lastAssistantMsg.metadata,
                            isNew: false
                        });
                    }
                }
            } catch (error) {
                console.error('Error fetching news history:', error);
            }
        };
        fetchHistory();
    }, []);

    const searchNews = async () => {
        if (!query.trim()) return;
        setLoading(true);
        setAnalysis(null);
        try {
            const response = await api.post('/news/search', { query });
            setArticles(response.data.results);
        } catch (error) {
            console.error('Error searching news:', error);
        } finally {
            setLoading(false);
        }
    };

    const analyzeArticle = async (article) => {
        setAnalyzing(article.url);
        setAnalysis(null); // Clear previous analysis
        try {
            // Send to chat agent for synthesis
            const prompt = `Analyze this news article:\nTitle: ${article.title}\nContent: ${article.content}`;
            const assistantMsg = {
                role: 'assistant',
                content: response.response,
                metadata: response.metadata,
                isNew: true
            };
            setAnalysis({
                article,
                ...assistantMsg
            });
            setHistory(prev => [...prev,
            { role: 'user', content: prompt, metadata: { article_title: article.title } },
                assistantMsg
            ]);
        } catch (error) {
            console.error('Error analyzing article:', error);
        } finally {
            setAnalyzing(null);
        }
    };

    return (
        <div className="p-6 h-full flex flex-col space-y-6 overflow-hidden bg-gray-50">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-gray-800 mb-1">Financial News</h2>
                    <p className="text-sm text-gray-500 italic">Get live insights and AI-driven impact analysis</p>
                </div>
                <div className="bg-white px-3 py-1 rounded-full border border-gray-200 shadow-sm">
                    <span className="text-xs font-semibold text-primary-600">⚡ Live Market Intelligence</span>
                </div>
            </div>

            {/* Search Bar */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
                <div className="flex space-x-3">
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && searchNews()}
                        placeholder="Search for companies, markets, or trends (e.g., 'Tata Motors', 'Nifty Bank')..."
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                    <button
                        onClick={searchNews}
                        disabled={loading}
                        className="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:bg-gray-300 transition-all font-semibold shadow-sm active:scale-95"
                    >
                        {loading ? 'Searching...' : 'Fetch News'}
                    </button>
                </div>
            </div>

            <div className="flex-1 flex space-x-6 overflow-hidden">
                {/* Article List */}
                <div className="w-1/2 overflow-y-auto space-y-4 pr-2 custom-scrollbar">
                    {articles.length === 0 && !loading && (
                        <div className="h-48 flex flex-col items-center justify-center text-gray-400 bg-white border border-dashed border-gray-300 rounded-xl">
                            <span className="text-3xl mb-2">📡</span>
                            <p className="text-sm">Search to fetch the latest financial news articles</p>
                        </div>
                    )}

                    {loading && (
                        <div className="space-y-4">
                            {[1, 2, 3].map(i => (
                                <div key={i} className="bg-white rounded-xl p-4 border border-gray-200 animate-pulse">
                                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-3"></div>
                                    <div className="h-3 bg-gray-100 rounded w-1/2 mb-4"></div>
                                    <div className="h-20 bg-gray-50 rounded mb-4"></div>
                                    <div className="h-8 bg-gray-100 rounded"></div>
                                </div>
                            ))}
                        </div>
                    )}

                    {articles.map((article, idx) => (
                        <div key={idx} className={`bg-white rounded-xl shadow-sm border p-4 transition-all ${analyzing === article.url ? 'ring-2 ring-primary-500 border-transparent' : 'border-gray-200 hover:shadow-md'}`}>
                            <h3 className="font-semibold text-gray-800 mb-2 leading-tight">{article.title}</h3>
                            <div className="flex items-center justify-between mb-3">
                                <a href={article.url} target="_blank" rel="noopener noreferrer" className="text-[10px] font-bold text-primary-500 hover:text-primary-700 uppercase tracking-tight">
                                    View Source ↗
                                </a>
                            </div>
                            <p className="text-sm text-gray-600 mb-4 line-clamp-3">{article.content}</p>
                            <button
                                onClick={() => analyzeArticle(article)}
                                disabled={analyzing}
                                className={`text-sm px-4 py-2 rounded-lg font-bold transition-all w-full flex items-center justify-center space-x-2 ${analyzing === article.url
                                    ? 'bg-primary-50 text-primary-700 cursor-default'
                                    : 'bg-primary-500 text-white hover:bg-primary-600'}`}
                            >
                                {analyzing === article.url ? (
                                    <>
                                        <div className="w-3 h-3 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
                                        <span>Analyzing Impact...</span>
                                    </>
                                ) : (
                                    <>
                                        <span>⚡ AI Impact Analysis</span>
                                    </>
                                )}
                            </button>
                        </div>
                    ))}
                </div>

                {/* Analysis View */}
                <div className="w-1/2 bg-white rounded-xl shadow-md border border-gray-200 p-0 overflow-hidden flex flex-col">
                    <div className="bg-gray-50 px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                        <span className="text-sm font-bold text-gray-700 flex items-center">
                            <span className="mr-2">🧠</span> AI INSIGHTS
                        </span>
                        {analyzing && <span className="text-[10px] bg-primary-100 text-primary-700 px-2 py-0.5 rounded-full font-bold animate-pulse">PROCESSING</span>}
                    </div>

                    <div className="flex-1 p-6 overflow-y-auto">
                        {analyzing ? (
                            <div className="h-full flex flex-col items-center justify-center space-y-6">
                                <div className="p-4 bg-primary-50 rounded-2xl shadow-inner border border-primary-100 w-full">
                                    <LoadingStatus />
                                </div>
                            </div>
                        ) : analysis ? (
                            <div className="animate-slide-in">
                                <div className="mb-6">
                                    <h3 className="font-bold text-lg text-gray-900 leading-tight mb-1">{analysis.article?.title || 'Selected Analysis'}</h3>
                                    <div className="h-1 w-12 bg-primary-500 rounded-full"></div>
                                </div>
                                <div className="space-y-4">
                                    {analysis.metadata?.visualizations && analysis.metadata.visualizations.map((viz, vIdx) => (
                                        <ChartRenderer key={vIdx} visualization={viz} />
                                    ))}
                                    <div className="prose prose-sm max-w-none text-gray-700">
                                        {analysis.isNew ? (
                                            <TypewriterText
                                                text={analysis.content}
                                                delay={3}
                                                onComplete={() => setAnalysis(prev => ({ ...prev, isNew: false }))}
                                            />
                                        ) : (
                                            <div className="whitespace-pre-wrap">{analysis.content}</div>
                                        )}
                                    </div>
                                </div>
                                <div className="mt-8 pt-6 border-t border-gray-100 flex items-center text-[10px] text-gray-400 font-medium">
                                    <span>ANALYSIS COMPLETED BY NEWS AGENT • {new Date().toLocaleTimeString()}</span>
                                </div>
                            </div>
                        ) : (
                            <div className="h-full flex flex-col items-center justify-center text-gray-400 p-8 text-center space-y-4">
                                <div className="w-20 h-20 bg-gray-50 rounded-full flex items-center justify-center text-4xl grayscale opacity-50">
                                    💡
                                </div>
                                <div>
                                    <p className="font-bold text-gray-600">No Active Analysis</p>
                                    <p className="text-xs">Select any news article on the left and click "AI Impact Analysis" to understand how it might affect the markets.</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* History Sidebar */}
                <div className="w-64 bg-white rounded-xl shadow-sm border border-gray-200 flex flex-col overflow-hidden">
                    <div className="p-4 border-b border-gray-100 bg-gray-50/50">
                        <h4 className="text-xs font-bold text-gray-500 uppercase">Recent Analyses</h4>
                    </div>
                    <div className="flex-1 overflow-y-auto p-2 space-y-2">
                        {history.filter(m => m.role === 'assistant').reverse().map((m, i) => {
                            const msgIdx = history.indexOf(m);
                            const userMsg = msgIdx > 0 ? history[msgIdx - 1] : null;
                            const title = userMsg?.metadata?.article_title;

                            return (
                                <button
                                    key={i}
                                    onClick={() => setAnalysis({ ...m, article: title ? { title } : null, isNew: false })}
                                    className="w-full text-left p-2 rounded-lg hover:bg-gray-50 text-xs text-gray-600 border border-transparent hover:border-gray-100"
                                >
                                    <p className="font-bold text-[10px] mb-1 text-primary-600 uppercase tracking-tight">
                                        {title || 'Analysis'}
                                    </p>
                                    <p className="line-clamp-2">{m.content.substring(0, 100)}...</p>
                                </button>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default NewsDashboard;
