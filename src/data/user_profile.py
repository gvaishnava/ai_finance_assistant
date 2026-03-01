"""
User profile and preferences
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

class RiskTolerance(Enum):
    """Risk tolerance levels"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

class InvestmentGoal(Enum):
    """Investment goal types"""
    RETIREMENT = "retirement"
    WEALTH_BUILDING = "wealth_building"
    EDUCATION = "education"
    HOME_PURCHASE = "home_purchase"
    SHORT_TERM_SAVINGS = "short_term_savings"
    OTHER = "other"

@dataclass
class Goal:
    """Represents a financial goal"""
    name: str
    goal_type: InvestmentGoal
    target_amount: float
    target_date: Optional[str] = None  # ISO format date
    current_amount: float = 0.0
    priority: int = 1  # 1-5, 1 being highest

@dataclass
class UserProfile:
    """User profile with preferences and goals"""
    user_id: str
    risk_tolerance: RiskTolerance = RiskTolerance.MODERATE
    investment_goals: List[Goal] = field(default_factory=list)
    knowledge_level: str = "beginner"  # beginner, intermediate, advanced
    monthly_investment_capacity: Optional[float] = None
    preferences: Dict = field(default_factory=dict)
    
    def add_goal(self, goal: Goal):
        """Add a financial goal"""
        self.investment_goals.append(goal)
    
    def remove_goal(self, goal_name: str):
        """Remove a goal by name"""
        self.investment_goals = [g for g in self.investment_goals if g.name != goal_name]
    
    def get_goal_progress(self, goal_name: str) -> Optional[float]:
        """
        Get progress percentage for a goal
        
        Args:
            goal_name: Name of the goal
            
        Returns:
            Progress percentage (0-100) or None if goal not found
        """
        for goal in self.investment_goals:
            if goal.name == goal_name:
                if goal.target_amount > 0:
                    return (goal.current_amount / goal.target_amount) * 100
                return 0.0
        return None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'user_id': self.user_id,
            'risk_tolerance': self.risk_tolerance.value,
            'investment_goals': [
                {
                    'name': g.name,
                    'goal_type': g.goal_type.value,
                    'target_amount': g.target_amount,
                    'target_date': g.target_date,
                    'current_amount': g.current_amount,
                    'priority': g.priority,
                }
                for g in self.investment_goals
            ],
            'knowledge_level': self.knowledge_level,
            'monthly_investment_capacity': self.monthly_investment_capacity,
            'preferences': self.preferences,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UserProfile':
        """Create from dictionary"""
        goals = [
            Goal(
                name=g['name'],
                goal_type=InvestmentGoal(g['goal_type']),
                target_amount=g['target_amount'],
                target_date=g.get('target_date'),
                current_amount=g.get('current_amount', 0.0),
                priority=g.get('priority', 1),
            )
            for g in data.get('investment_goals', [])
        ]
        
        return cls(
            user_id=data['user_id'],
            risk_tolerance=RiskTolerance(data.get('risk_tolerance', 'moderate')),
            investment_goals=goals,
            knowledge_level=data.get('knowledge_level', 'beginner'),
            monthly_investment_capacity=data.get('monthly_investment_capacity'),
            preferences=data.get('preferences', {}),
        )
