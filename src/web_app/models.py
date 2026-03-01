"""
Pydantic models for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

# Request models

class ChatRequest(BaseModel):
    """Chat message request"""
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    source: Optional[str] = Field(None, description="Source component/tab (e.g., chat, tax, portfolio)")
    metadata: Optional[Dict] = Field(None, description="Optional metadata (e.g., article title)")
    
class PortfolioHolding(BaseModel):
    """Single portfolio holding"""
    symbol: str = Field(..., description="Stock symbol (e.g., RELIANCE.NS)")
    quantity: float = Field(..., gt=0, description="Number of shares")
    average_price: Optional[float] = Field(None, description="Average purchase price")
    
class PortfolioRequest(BaseModel):
    """Portfolio analysis request"""
    holdings: List[PortfolioHolding]
    message: Optional[str] = Field("Analyze my portfolio", description="Optional query")
    session_id: Optional[str] = None

class GoalRequest(BaseModel):
    """Financial goal request"""
    name: str
    goal_type: str  # retirement, wealth_building, etc.
    target_amount: float
    target_date: Optional[str] = None
    current_amount: float = 0.0
    message: Optional[str] = Field("Help me with this goal", description="Optional query")
    session_id: Optional[str] = None
    metadata: Optional[Dict] = Field(None, description="Optional metadata (e.g., goal name)")

class UserProfileUpdate(BaseModel):
    """User profile update"""
    risk_tolerance: Optional[str] = None  # conservative, moderate, aggressive
    knowledge_level: Optional[str] = None  # beginner, intermediate, advanced
    monthly_investment_capacity: Optional[float] = None

# Response models

class CitationModel(BaseModel):
    """Citation information"""
    index: int
    source: str
    page: Optional[int] = None
    module: Optional[str] = None
    score: float

class ChatResponse(BaseModel):
    """Chat response"""
    response: str
    agent: str
    agent_display_name: str
    session_id: str
    citations: Optional[List[CitationModel]] = None
    metadata: Optional[Dict] =None
    timestamp: datetime = Field(default_factory=datetime.now)

class ConversationMessage(BaseModel):
    """Conversation history message"""
    role: str  # user or assistant
    content: str
    agent: Optional[str] = None
    source: Optional[str] = None
    metadata: Optional[Dict] = None
    timestamp: str

class ConversationHistoryResponse(BaseModel):
    """Conversation history"""
    session_id: str
    messages: List[ConversationMessage]
    
class StockQuote(BaseModel):
    """Stock quote information"""
    symbol: str
    name: str
    price: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[int] = None
    market_cap: Optional[float] = None
    sector: Optional[str] = None
    currency: str = "INR"  # Default to INR if not specified

class MarketTrendsResponse(BaseModel):
    """Market trends/indices"""
    indices: List[StockQuote]
    timestamp: datetime = Field(default_factory=datetime.now)

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    vector_store_loaded: bool
    num_documents: int
