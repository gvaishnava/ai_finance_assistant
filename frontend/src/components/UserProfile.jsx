import React, { useState, useEffect } from 'react';
import { getUserProfile, updateUserProfile } from '../services/api';

const UserProfile = () => {
    const [profile, setProfile] = useState({
        risk_tolerance: 'moderate',
        knowledge_level: 'beginner',
        monthly_investment_capacity: '',
    });
    const [loading, setLoading] = useState(false);
    const [saved, setSaved] = useState(false);

    useEffect(() => {
        fetchProfile();
    }, []);

    const fetchProfile = async () => {
        try {
            const data = await getUserProfile();
            if (data.profile) {
                setProfile({
                    risk_tolerance: data.profile.risk_tolerance || 'moderate',
                    knowledge_level: data.profile.knowledge_level || 'beginner',
                    monthly_investment_capacity: data.profile.monthly_investment_capacity || '',
                });
            }
        } catch (error) {
            console.error('Error fetching profile:', error);
        }
    };

    const handleSave = async () => {
        setLoading(true);
        setSaved(false);
        try {
            await updateUserProfile(profile);
            setSaved(true);
            setTimeout(() => setSaved(false), 3000);
        } catch (error) {
            console.error('Error saving profile:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-6 space-y-6 h-full overflow-y-auto custom-scrollbar">
            <div>
                <h2 className="text-2xl font-bold text-gray-800 mb-1">User Profile</h2>
                <p className="text-sm text-gray-500">Customize your financial learning experience</p>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-6">
                {/* Knowledge Level */}
                <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Knowledge Level
                    </label>
                    <div className="grid grid-cols-3 gap-3">
                        {['beginner', 'intermediate', 'advanced'].map((level) => (
                            <button
                                key={level}
                                onClick={() => setProfile({ ...profile, knowledge_level: level })}
                                className={`px-4 py-3 rounded-lg border-2 font-semibold transition-all ${profile.knowledge_level === level
                                    ? 'border-primary-500 bg-primary-50 text-primary-700'
                                    : 'border-gray-200 hover:border-gray-300 text-gray-700'
                                    }`}
                            >
                                {level.charAt(0).toUpperCase() + level.slice(1)}
                            </button>
                        ))}
                    </div>
                    <p className="text-xs text-gray-500 mt-2">
                        This helps the AI adjust explanations to your understanding level
                    </p>
                </div>

                {/* Risk Tolerance */}
                <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Risk Tolerance
                    </label>
                    <div className="grid grid-cols-3 gap-3">
                        {['conservative', 'moderate', 'aggressive'].map((risk) => (
                            <button
                                key={risk}
                                onClick={() => setProfile({ ...profile, risk_tolerance: risk })}
                                className={`px-4 py-3 rounded-lg border-2 font-semibold transition-all ${profile.risk_tolerance === risk
                                    ? 'border-primary-500 bg-primary-50 text-primary-700'
                                    : 'border-gray-200 hover:border-gray-300 text-gray-700'
                                    }`}
                            >
                                {risk.charAt(0).toUpperCase() + risk.slice(1)}
                            </button>
                        ))}
                    </div>
                    <p className="text-xs text-gray-500 mt-2">
                        Your comfort level with investment risk
                    </p>
                </div>

                {/* Monthly Investment Capacity */}
                <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Monthly Investment Capacity (Optional)
                    </label>
                    <div className="relative">
                        <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500">₹</span>
                        <input
                            type="number"
                            value={profile.monthly_investment_capacity}
                            onChange={(e) => setProfile({ ...profile, monthly_investment_capacity: e.target.value })}
                            placeholder="10000"
                            className="w-full pl-8 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        />
                    </div>
                    <p className="text-xs text-gray-500 mt-2">
                        This helps with personalized goal planning
                    </p>
                </div>

                {/* Save Button */}
                <div className="pt-4 border-t border-gray-200">
                    <button
                        onClick={handleSave}
                        disabled={loading}
                        className="w-full px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:bg-gray-300 transition-colors font-semibold flex items-center justify-center space-x-2"
                    >
                        {loading ? (
                            <>
                                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                                <span>Saving...</span>
                            </>
                        ) : saved ? (
                            <>
                                <span>✓</span>
                                <span>Saved!</span>
                            </>
                        ) : (
                            <span>Save Profile</span>
                        )}
                    </button>
                </div>
            </div>

            {/* Info */}
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                <div className="flex items-start space-x-3">
                    <div className="text-2xl">🔒</div>
                    <div>
                        <h4 className="font-semibold text-blue-900 mb-1">Privacy</h4>
                        <p className="text-sm text-blue-700">
                            Your preferences are stored locally in your browser session and help personalize your learning experience.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default UserProfile;
