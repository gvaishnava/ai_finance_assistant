import React, { useState, useEffect } from 'react';
import { sendGoalMessage, getFullSession, getChatHistory } from '../services/api';
import { TypewriterText, LoadingStatus, ChartRenderer } from './UIComponents';

const GoalPlanner = () => {
    const [goals, setGoals] = useState([]);
    const [messages, setMessages] = useState([]);
    const [activeAnalysis, setActiveAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [analysis, setAnalysis] = useState(null);
    const [showForm, setShowForm] = useState(false);
    const [activeGoalName, setActiveGoalName] = useState(null);

    const [newGoal, setNewGoal] = useState({
        name: '',
        goal_type: 'retirement',
        target_amount: '',
        target_date: '',
        current_amount: '',
        message: 'Give me a detailed plan to reach this goal.'
    });

    useEffect(() => {
        const fetchSavedGoals = async () => {
            try {
                const data = await getFullSession();
                if (data.goals) {
                    setGoals(data.goals);
                }

                const historyData = await getChatHistory('goal_planning');
                if (historyData.messages && historyData.messages.length > 0) {
                    setMessages(historyData.messages.map(m => ({ ...m, isNew: false })));
                    // Set active goal to most recent one from history if none active
                    const lastUserMsg = [...historyData.messages].reverse().find(m => m.role === 'user' && m.metadata?.goal_name);
                    if (lastUserMsg) {
                        setActiveGoalName(lastUserMsg.metadata.goal_name);
                    }
                }
            } catch (error) {
                console.error('Error fetching saved goals:', error);
            }
        };
        fetchSavedGoals();
    }, []);

    const goalTypes = [
        { id: 'retirement', label: 'Retirement', icon: '🏖️' },
        { id: 'wealth_building', label: 'Wealth Building', icon: '📈' },
        { id: 'education', label: 'Education', icon: '🎓' },
        { id: 'home', label: 'New Home', icon: '🏠' },
        { id: 'emergency', label: 'Emergency Fund', icon: '🛡️' },
    ];

    const handleAddGoal = async (e) => {
        e.preventDefault();
        setLoading(true);
        setAnalysis(null);

        try {
            const goalWithMeta = { ...newGoal, metadata: { goal_name: newGoal.name } };
            const result = await sendGoalMessage(goalWithMeta, newGoal.message);
            setActiveGoalName(newGoal.name);

            // Add to local list if not already there (based on name)
            setGoals(prev => {
                const exists = prev.find(g => g.name === newGoal.name);
                if (exists) {
                    return prev.map(g => g.name === newGoal.name ? { ...newGoal } : g);
                }
                return [...prev, { ...newGoal }];
            });

            setAnalysis({
                name: newGoal.name,
                content: result.response,
                agent: result.agent_display_name,
                metadata: result.metadata
            });

            setShowForm(false);
            setNewGoal(prev => ({ ...prev, name: '', target_amount: '', target_date: '', current_amount: '' }));
            setMessages(prev => [...prev,
            { role: 'user', content: newGoal.message, metadata: { goal_name: newGoal.name } },
            {
                role: 'assistant',
                content: result.response,
                agent: result.agent_display_name,
                metadata: result.metadata,
                isNew: true
            }
            ]);
        } catch (error) {
            console.error('Error adding goal:', error);
        } finally {
            setLoading(false);
        }
    };

    const runAnalysis = async (goal) => {
        setLoading(true);
        setAnalysis(null);
        setActiveGoalName(goal.name);
        try {
            const goalWithMeta = { ...goal, metadata: { goal_name: goal.name } };
            const result = await sendGoalMessage(goalWithMeta, "Analyze my progress towards this goal.");
            setAnalysis({
                name: goal.name,
                content: result.response,
                agent: result.agent_display_name,
                metadata: result.metadata
            });
            setMessages(prev => [...prev,
            { role: 'user', content: "Analyze my progress towards this goal.", metadata: { goal_name: goal.name } },
            {
                role: 'assistant',
                content: result.response,
                agent: result.agent_display_name,
                metadata: result.metadata,
                isNew: true
            }
            ]);
        } catch (error) {
            console.error('Error analyzing goal:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-6 h-full flex flex-col space-y-6 overflow-hidden bg-gray-50">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-gray-800">Financial Goal Planner</h2>
                    <p className="text-sm text-gray-500 italic">Map out your future and get AI-driven milestones</p>
                </div>
                <button
                    onClick={() => setShowForm(!showForm)}
                    className="bg-primary-600 text-white px-4 py-2 rounded-lg font-bold shadow-md hover:bg-primary-700 transition-all flex items-center space-x-2"
                >
                    <span>{showForm ? '✕ Close' : '＋ Add New Goal'}</span>
                </button>
            </div>

            <div className="flex-1 flex space-x-6 overflow-hidden">
                {/* Left Side: Goal Form or List */}
                <div className="w-1/2 flex flex-col space-y-4 overflow-y-auto pr-2 custom-scrollbar">
                    {showForm ? (
                        <div className="bg-white rounded-xl shadow-lg border border-primary-100 p-6 animate-slide-in">
                            <h3 className="text-lg font-bold text-gray-800 mb-4 border-b pb-2">Create Financial Goal</h3>
                            <form onSubmit={handleAddGoal} className="space-y-4">
                                <div>
                                    <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Goal Name</label>
                                    <input
                                        required
                                        type="text"
                                        placeholder="e.g. Early Retirement"
                                        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                                        value={newGoal.name}
                                        onChange={e => setNewGoal({ ...newGoal, name: e.target.value })}
                                    />
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Type</label>
                                        <select
                                            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                                            value={newGoal.goal_type}
                                            onChange={e => setNewGoal({ ...newGoal, goal_type: e.target.value })}
                                        >
                                            {goalTypes.map(t => <option key={t.id} value={t.id}>{t.label}</option>)}
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Target Date</label>
                                        <input
                                            required
                                            type="date"
                                            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                                            value={newGoal.target_date}
                                            onChange={e => setNewGoal({ ...newGoal, target_date: e.target.value })}
                                        />
                                    </div>
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Target Amount (₹)</label>
                                        <input
                                            required
                                            type="number"
                                            placeholder="5,000,000"
                                            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                                            value={newGoal.target_amount}
                                            onChange={e => setNewGoal({ ...newGoal, target_amount: e.target.value })}
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Already Saved (₹)</label>
                                        <input
                                            required
                                            type="number"
                                            placeholder="500,000"
                                            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                                            value={newGoal.current_amount}
                                            onChange={e => setNewGoal({ ...newGoal, current_amount: e.target.value })}
                                        />
                                    </div>
                                </div>
                                <div className="pt-2">
                                    <button
                                        type="submit"
                                        className="w-full bg-primary-600 text-white py-3 rounded-xl font-bold shadow-lg hover:bg-primary-700 transition-all active:scale-95"
                                    >
                                        Set Goal & Analyze
                                    </button>
                                </div>
                            </form>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {goals.length === 0 ? (
                                <div className="h-64 flex flex-col items-center justify-center text-gray-400 bg-white border border-dashed border-gray-300 rounded-xl p-8 text-center">
                                    <span className="text-4xl mb-4">🎯</span>
                                    <p className="font-bold text-gray-600">No Goals Defined Yet</p>
                                    <p className="text-xs mb-6">Financial freedom starts with a plan. Add your first goal to get started.</p>
                                    <button
                                        onClick={() => setShowForm(true)}
                                        className="text-primary-600 font-bold border-2 border-primary-600 px-4 py-2 rounded-lg hover:bg-primary-50 transition-all"
                                    >
                                        + Create My First Goal
                                    </button>
                                </div>
                            ) : (
                                goals.map((goal, idx) => (
                                    <div key={idx} className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:border-primary-300 transition-all group">
                                        <div className="flex items-start justify-between">
                                            <div className="flex items-center space-x-3">
                                                <div className="w-12 h-12 bg-primary-50 rounded-xl flex items-center justify-center text-2xl">
                                                    {goalTypes.find(t => t.id === goal.goal_type)?.icon || '💰'}
                                                </div>
                                                <div>
                                                    <h4 className="font-bold text-gray-800">{goal.name}</h4>
                                                    <p className="text-[10px] text-gray-400 uppercase font-bold tracking-wider">
                                                        {goal.goal_type.replace('_', ' ')}
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <p className="text-sm font-bold text-gray-700">₹{parseFloat(goal.target_amount).toLocaleString()}</p>
                                                <p className="text-[10px] text-gray-400">Target: {new Date(goal.target_date).toLocaleDateString()}</p>
                                            </div>
                                        </div>

                                        <div className="mt-4">
                                            <div className="flex justify-between text-[10px] font-bold text-gray-500 mb-1">
                                                <span>Progress</span>
                                                <span>{Math.round((goal.current_amount / goal.target_amount) * 100)}%</span>
                                            </div>
                                            <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                                                <div
                                                    className="bg-primary-500 h-full rounded-full transition-all duration-1000"
                                                    style={{ width: `${Math.min(100, (goal.current_amount / goal.target_amount) * 100)}%` }}
                                                ></div>
                                            </div>
                                        </div>

                                        <div className="mt-4 flex space-x-2">
                                            <button
                                                onClick={() => runAnalysis(goal)}
                                                disabled={loading}
                                                className={`flex-1 text-[10px] py-2 rounded-lg font-bold transition-all border flex items-center justify-center space-x-1 ${activeGoalName === goal.name && loading
                                                    ? 'bg-primary-100 text-primary-400 border-primary-100 cursor-not-allowed'
                                                    : 'bg-primary-50 text-primary-600 border-transparent hover:border-primary-200'}`}
                                            >
                                                <span>📊</span>
                                                <span>{activeGoalName === goal.name && loading ? 'Analyzing...' : 'Analyze'}</span>
                                            </button>
                                            <button
                                                onClick={() => setActiveGoalName(goal.name)}
                                                className={`flex-1 text-[10px] py-2 rounded-lg font-bold transition-all border flex items-center justify-center space-x-1 ${activeGoalName === goal.name
                                                    ? 'bg-primary-500 text-white border-primary-500 shadow-sm'
                                                    : 'bg-gray-50 text-gray-600 border-transparent hover:border-gray-200'}`}
                                            >
                                                <span>📂</span>
                                                <span>History</span>
                                            </button>
                                            <button
                                                onClick={() => {
                                                    setNewGoal(goal);
                                                    setShowForm(true);
                                                }}
                                                className="px-3 py-2 bg-gray-50 text-gray-400 rounded-lg hover:text-gray-600 border border-transparent hover:border-gray-200 transition-all"
                                            >
                                                ✏️
                                            </button>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    )}

                    <div className="bg-yellow-50 border border-yellow-100 rounded-xl p-4 text-xs text-yellow-800 shadow-inner">
                        <div className="flex space-x-2">
                            <span>💡</span>
                            <p><strong>Pro Tip:</strong> Be realistic with your target dates. The AI uses these dates to calculate required returns and risk appetite.</p>
                        </div>
                    </div>
                </div>

                {/* Right Side: AI Advice */}
                <div className="w-1/2 bg-white rounded-2xl shadow-xl border border-gray-200 flex flex-col overflow-hidden relative">
                    <div className="bg-gray-50 px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                        <span className="text-sm font-bold text-gray-700 flex items-center uppercase tracking-widest">
                            <span className="mr-2">🧠</span> {activeGoalName ? `${activeGoalName} PLAN` : 'General Planning'}
                        </span>
                        {loading && <span className="text-[10px] bg-primary-100 text-primary-700 px-2 py-0.5 rounded-full font-bold animate-pulse">MODEL THINKING</span>}
                    </div>

                    <div className="flex-1 p-6 overflow-y-auto custom-scrollbar space-y-6">
                        {loading && messages.length === 0 ? (
                            <div className="h-full flex flex-col items-center justify-center">
                                <div className="w-full max-w-sm">
                                    <LoadingStatus />
                                </div>
                            </div>
                        ) : (() => {
                            const filteredMessages = activeGoalName
                                ? messages.filter((m, idx) => {
                                    // Match if this message has the goal_name
                                    if (m.metadata?.goal_name === activeGoalName) return true;
                                    // Or if it's an assistant message following a user message for this goal
                                    if (m.role === 'assistant' && idx > 0) {
                                        const prev = messages[idx - 1];
                                        if (prev.role === 'user' && prev.metadata?.goal_name === activeGoalName) return true;
                                    }
                                    return false;
                                })
                                : messages;

                            if (filteredMessages.length === 0 && !loading) {
                                return (
                                    <div className="h-full flex flex-col items-center justify-center text-center p-8 space-y-4">
                                        <div className="w-16 h-16 bg-gray-50 rounded-2xl flex items-center justify-center text-3xl grayscale opacity-30 border border-gray-100">
                                            {activeGoalName ? '📊' : '💡'}
                                        </div>
                                        {activeGoalName ? (
                                            <div>
                                                <h4 className="font-bold text-gray-600">No specific history for {activeGoalName}</h4>
                                                <p className="text-xs text-gray-400">Click "Analysis" to generate a plan for this goal.</p>
                                            </div>
                                        ) : (
                                            <>
                                                <div className="mt-4 flex flex-wrap gap-2">
                                                    <button
                                                        onClick={() => setActiveGoalName(null)}
                                                        className="text-[10px] font-bold text-primary-600 hover:underline"
                                                    >
                                                        VIEW GLOBAL PLANNING HISTORY
                                                    </button>
                                                </div>
                                                <div>
                                                    <h4 className="font-bold text-gray-600">No Goal Selected</h4>
                                                    <p className="text-xs text-gray-400 max-w-[200px] mx-auto">Select a goal from the left to see its specific analysis and chat history.</p>
                                                </div>
                                            </>
                                        )}
                                    </div>
                                );
                            }

                            return (
                                <div className="space-y-6">
                                    {filteredMessages.map((msg, idx) => (
                                        <div key={idx} className="animate-slide-in">
                                            <div className="flex items-center space-x-2 mb-3">
                                                <div className="h-px flex-1 bg-gray-100"></div>
                                                <span className="text-[10px] font-bold text-gray-300 uppercase tracking-tighter">
                                                    {msg.role === 'user' ? 'Your Query' : `Analysis for goal`}
                                                </span>
                                                <div className="h-px flex-1 bg-gray-100"></div>
                                            </div>
                                            <div className={`p-4 rounded-xl ${msg.role === 'user' ? 'bg-primary-50 text-primary-900 border border-primary-100' : 'bg-white text-gray-800'}`}>
                                                {msg.metadata?.visualizations && msg.metadata.visualizations.map((viz, vIdx) => (
                                                    <ChartRenderer key={vIdx} visualization={viz} />
                                                ))}
                                                <div className="prose prose-sm max-w-none">
                                                    {msg.role === 'assistant' && idx === filteredMessages.length - 1 && loading ? (
                                                        <LoadingStatus />
                                                    ) : (
                                                        <div className="whitespace-pre-wrap">
                                                            {msg.role === 'assistant' && msg.isNew && !loading
                                                                ? <TypewriterText
                                                                    text={msg.content}
                                                                    delay={10}
                                                                    onComplete={() => {
                                                                        setMessages(prev => prev.map((m, i) => {
                                                                            if (m.content === msg.content && m.role === 'assistant') {
                                                                                return { ...m, isNew: false };
                                                                            }
                                                                            return m;
                                                                        }));
                                                                    }}
                                                                />
                                                                : msg.content
                                                            }
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                    {loading && filteredMessages.length > 0 && filteredMessages[filteredMessages.length - 1].role === 'user' && (
                                        <div className="animate-slide-in">
                                            <div className="flex items-center space-x-2 mb-3">
                                                <div className="h-px flex-1 bg-gray-100"></div>
                                                <span className="text-[10px] font-bold text-gray-300 uppercase">Thinking...</span>
                                                <div className="h-px flex-1 bg-gray-100"></div>
                                            </div>
                                            <LoadingStatus />
                                        </div>
                                    )}
                                </div>
                            );
                        })()}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default GoalPlanner;
