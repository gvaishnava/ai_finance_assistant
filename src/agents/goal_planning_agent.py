"""
Goal Planning Agent - Assists with financial goal setting and planning
"""

import asyncio
from typing import Dict, Optional
from datetime import datetime
from src.agents.base_agent import BaseAgent
from src.utils.formatters import format_currency
from src.utils.logger import get_logger
from src.utils.visualizers import get_goal_projection_chart, get_goals_summary_chart

logger = get_logger(__name__)


class GoalPlanningAgent(BaseAgent):
    """Agent for financial goal setting and planning"""
    
    def __init__(self, config_path: str = "config.yaml"):
        super().__init__(
            agent_name="goal_planning",
            config_path=config_path,
            use_rag=True
        )
    
    def process(
        self,
        query: str,
        context: Optional[Dict] = None,
        **kwargs
    ) -> Dict:
        """
        Help with goal planning
        
        Args:
            query: User query about financial goals
            context: Context including user profile
            **kwargs: Additional parameters (goal data)
            
        Returns:
            Response dictionary with goal planning insights
        """
        logger.info(f"Goal Planning Agent processing: {query[:50]}...")
        
        # Get user profile and goals
        user_profile = (context or {}).get('user_profile', {})
        goals = (context or {}).get('goals') or user_profile.get('investment_goals', [])
        
        # Check if this is about a specific goal (passed via kwargs)
        goal_data = kwargs.get('goal')
        
        # If no explicit goal in kwargs, check if the query mentions one from the list
        if not goal_data and goals:
            # Try to find a goal whose name is in the query
            for g in goals:
                if g.get('name', '').lower() in query.lower():
                    goal_data = g
                    break
            
            # If still no goal found but it's a "Help me plan for..." query and only one goal exists, use that
            if not goal_data and len(goals) == 1:
                goal_data = goals[0]

        if goal_data:
            return self._analyze_specific_goal(query, goal_data, user_profile)
        elif goals:
            return self._review_existing_goals(query, goals, user_profile)
        else:
            return self._general_goal_planning(query, user_profile)
    
    def _analyze_specific_goal(
        self,
        query: str,
        goal: Dict,
        user_profile: Dict
    ) -> Dict:
        """Analyze a specific financial goal"""
        
        target_amount = goal.get('target_amount', 0)
        current_amount = goal.get('current_amount', 0)
        target_date = goal.get('target_date')
        goal_name = goal.get('name', 'Your goal')
        
        # Calculate remaining amount and time
        remaining = target_amount - current_amount
        progress_pct = (current_amount / target_amount * 100) if target_amount > 0 else 0
        
        goal_summary = f"""**Goal: {goal_name}**

- Target Amount: {format_currency(target_amount)}
- Current Amount: {format_currency(current_amount)}
- Remaining: {format_currency(remaining)}
- Progress: {progress_pct:.1f}%
"""
        
        if target_date:
            try:
                # Handle different date formats
                date_str = target_date.replace('/', '-')
                if 'T' in date_str:
                    date_str = date_str.split('T')[0]
                target_dt = datetime.fromisoformat(date_str)
                months_remaining = ((target_dt - datetime.now()).days) / 30
                
                if months_remaining > 0:
                    monthly_required = remaining / months_remaining
                    goal_summary += f"- Time Remaining: {months_remaining:.0f} months\n"
                    goal_summary += f"- Monthly Savings Needed: {format_currency(monthly_required)}\n"
            except Exception as e:
                logger.warning(f"Error parsing date {target_date}: {e}")
        
        # Retrieve educational context
        edu_context = self.retrieve_context(
            f"financial planning goal-based investing {goal.get('goal_type', '')}",
            top_k=3
        )
        
        # Special encouragement for $0 balances
        zero_balance_note = ""
        if current_amount <= 0:
            zero_balance_note = "\nNote: You're starting at the very beginning! The first step is often the hardest, but having a clear target is half the battle."

        # Generate advice
        prompt = f"""{goal_summary}{zero_balance_note}

User Query: {query}

Provide educational guidance about:
1. Strategies for achieving this type of goal (e.g., {goal.get('goal_type', 'savings')})
2. Important concepts to understand (time value of money, compound interest, etc.)
3. General principles for goal-based investing
4. How to stay motivated even when starting from zero (if applicable)

Focus on financial education, not specific product recommendations."""
        
        response = self.generate_response(prompt, edu_context)
        full_response = f"{goal_summary}\n**Planning Insights:**\n\n{response}"
        
        # Prepare visualization
        visualizations = [get_goal_projection_chart(goal)]
        
        return self.format_response(
            self.add_disclaimer(full_response, "general"),
            metadata={
                'goal_progress': progress_pct,
                'visualizations': visualizations
            }
        )
    
    def _review_existing_goals(
        self,
        query: str,
        goals: list,
        user_profile: Dict
    ) -> Dict:
        """Review all existing goals"""
        
        goals_summary = "**Your Financial Goals:**\n\n"
        
        for i, goal in enumerate(goals, 1):
            name = goal.get('name', f'Goal {i}')
            target = goal.get('target_amount', 0)
            current = goal.get('current_amount', 0)
            progress = (current / target * 100) if target > 0 else 0
            
            goals_summary += f"{i}. **{name}**: {format_currency(target)} ({progress:.0f}% complete)\n"
        
        # Retrieve educational context
        edu_context = self.retrieve_context(
            "financial goal planning prioritization",
            top_k=3
        )
        
        prompt = f"""{goals_summary}

User Query: {query}

Provide educational insights about:
1. Principles of goal prioritization
2. How to track progress effectively
3. Strategies for managing multiple financial goals

Focus on education and general principles."""
        
        response = self.generate_response(prompt, edu_context)
        full_response = f"{goals_summary}\n**Goal Planning Insights:**\n\n{response}"
        
        return self.format_response(
            self.add_disclaimer(full_response, "general"),
            metadata={'num_goals': len(goals), 'visualizations': [get_goals_summary_chart(goals)] if goals else []}
        )
    
    def _general_goal_planning(
        self,
        query: str,
        user_profile: Dict
    ) -> Dict:
        """General goal planning education"""
        
        # Retrieve educational context
        edu_context = self.retrieve_context(
            "financial goal setting planning SMART goals",
            top_k=5
        )
        
        prompt = f"""User Query: {query}

Provide comprehensive education about financial goal planning:
1. Importance of setting financial goals
2. Types of financial goals (short-term, medium-term, long-term)
3. How to set SMART financial goals
4. Basic strategies for achieving financial goals

Make it practical and actionable for beginners."""
        
        response = self.generate_response(prompt, edu_context)
        
        return self.format_response(
            self.add_disclaimer(response, "general"),
            citations=self.retriever.get_citations(query, top_k=5) if self.retriever else []
        )

    # ── Asynchronous ──────────────────────────────────────────────────────────

    async def async_process(
        self,
        query: str,
        context: Optional[Dict] = None,
        **kwargs,
    ) -> Dict:
        """Async goal planning"""
        logger.info(f"Goal Planning Agent async processing: {query[:50]}...")
        user_profile = (context or {}).get('user_profile', {})
        goals = (context or {}).get('goals') or user_profile.get('investment_goals', [])
        
        # Priority 1: Explicit goal passed in kwargs (from UI clicks)
        goal_data = kwargs.get('goal')
        
        # Priority 2: Match by name if provided in query or metadata
        if not goal_data:
            goal_name = kwargs.get('goal_name')
            if goal_name:
                goal_data = next((g for g in goals if g.get('name') == goal_name), None)
        
        # Priority 3: Fuzzy match in query
        if not goal_data and goals:
            for g in goals:
                if g.get('name', '').lower() in query.lower():
                    goal_data = g
                    break
            if not goal_data and len(goals) == 1:
                goal_data = goals[0]

        if goal_data:
            return await self._async_analyze_specific_goal(query, goal_data, user_profile)
        elif goals:
            return await self._async_review_existing_goals(query, goals, user_profile)
        return await self._async_general_goal_planning(query, user_profile)

    async def _async_analyze_specific_goal(self, query: str, goal: Dict, user_profile: Dict) -> Dict:
        target_amount = goal.get('target_amount', 0)
        current_amount = goal.get('current_amount', 0)
        target_date = goal.get('target_date')
        goal_name = goal.get('name', 'Your goal')
        remaining = target_amount - current_amount
        progress_pct = (current_amount / target_amount * 100) if target_amount > 0 else 0
        
        goal_summary = f"""**Goal: {goal_name}**

- Target Amount: {format_currency(target_amount)}
- Current Amount: {format_currency(current_amount)}
- Remaining: {format_currency(remaining)}
- Progress: {progress_pct:.1f}%
"""
        if target_date:
            try:
                date_str = target_date.replace('/', '-')
                if 'T' in date_str:
                    date_str = date_str.split('T')[0]
                target_dt = datetime.fromisoformat(date_str)
                months_remaining = ((target_dt - datetime.now()).days) / 30
                if months_remaining > 0:
                    monthly_required = remaining / months_remaining
                    goal_summary += f"- Time Remaining: {months_remaining:.0f} months\n"
                    goal_summary += f"- Monthly Savings Needed: {format_currency(monthly_required)}\n"
            except Exception as e:
                logger.warning(f"Error parsing date {target_date}: {e}")
        
        edu_context = self.retrieve_context(
            f"financial planning goal-based investing {goal.get('goal_type', '')}", top_k=3
        )
        
        zero_balance_note = ""
        if float(current_amount) <= 0:
            zero_balance_note = "\nNote: You're starting at the very beginning! The first step is often the hardest, but having a clear target is half the battle."

        prompt = f"""{goal_summary}{zero_balance_note}

User Query: {query}

Provide educational guidance about:
1. Strategies for achieving this type of goal (e.g., {goal.get('goal_type', 'savings')})
2. Important concepts to understand (time value of money, compound interest, etc.)
3. General principles for goal-based investing
4. How to start from zero and build momentum

Focus on financial education, not specific recommendations."""

        response = await self.async_generate_response(prompt, edu_context)
        full_response = f"{goal_summary}\n**Planning Insights:**\n\n{response}"
        
        # Prepare visualization
        visualizations = [get_goal_projection_chart(goal)]
        
        return self.format_response(
            self.add_disclaimer(full_response, "general"),
            metadata={
                'goal_progress': progress_pct,
                'visualizations': visualizations
            }
        )

    async def _async_review_existing_goals(self, query: str, goals: list, user_profile: Dict) -> Dict:
        goals_summary = "**Your Financial Goals:**\n\n"
        for i, goal in enumerate(goals, 1):
            name = goal.get('name', f'Goal {i}')
            target = goal.get('target_amount', 0)
            current = goal.get('current_amount', 0)
            progress = (current / target * 100) if target > 0 else 0
            goals_summary += f"{i}. **{name}**: {format_currency(target)} ({progress:.0f}% complete)\n"
        edu_context = self.retrieve_context("financial goal planning prioritization", top_k=3)
        prompt = f"""{goals_summary}\n\nUser Query: {query}\n\nProvide educational insights about:\n1. Principles of goal prioritization\n2. How to track progress effectively\n3. Strategies for managing multiple financial goals\n\nFocus on education and general principles."""
        response = await self.async_generate_response(prompt, edu_context)
        full_response = f"{goals_summary}\n**Goal Planning Insights:**\n\n{response}"
        return self.format_response(
            self.add_disclaimer(full_response, "general"),
            metadata={'num_goals': len(goals), 'visualizations': [get_goals_summary_chart(goals)] if goals else []}
        )

    async def _async_general_goal_planning(self, query: str, user_profile: Dict) -> Dict:
        edu_context = self.retrieve_context("financial goal setting planning SMART goals", top_k=5)
        prompt = f"""User Query: {query}\n\nProvide comprehensive education about financial goal planning:\n1. Importance of setting financial goals\n2. Types of financial goals (short-term, medium-term, long-term)\n3. How to set SMART financial goals\n4. Basic strategies for achieving financial goals\n\nMake it practical and actionable for beginners."""
        response = await self.async_generate_response(prompt, edu_context)
        return self.format_response(
            self.add_disclaimer(response, "general"),
            citations=self.retriever.get_citations(query, top_k=5) if self.retriever else []
        )
