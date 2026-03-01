import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml

from src.utils.logger import get_logger

logger = get_logger(__name__)

class Session:
    """Represents a user session"""
    
    def __init__(self, session_id: str = None):
        """
        Initialize a session
        
        Args:
            session_id: Optional existing session ID
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.created_at = datetime.now()
        self.last_accessed = datetime.now()
        self.messages: List[Dict[str, Any]] = []
        self.user_profile: Dict[str, Any] = {}
        self.portfolio: Dict[str, Any] = {}
        self.goals: List[Dict[str, Any]] = []
        self.state: Dict[str, Any] = {}
    
    def add_message(self, role: str, content: str, agent: str = None, metadata: Dict = None, source: str = None):
        """
        Add a message to the conversation history
        
        Args:
            role: Message role (user, assistant, system)
            content: Message content
            agent: Optional agent name that generated the response
            metadata: Optional metadata dictionary
            source: Optional source/tab identifier
        """
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
        }
        
        if agent:
            message['agent'] = agent
            
        if source:
            message['source'] = source
        
        if metadata:
            message['metadata'] = metadata
        
        self.messages.append(message)
        self.last_accessed = datetime.now()
    
    def get_conversation_history(self, limit: int = None, agent_filter: str = None, source_filter: str = None) -> List[Dict]:
        """
        Get conversation history with improved filtering for multiple tabs.
        
        Args:
            limit: Optional limit on number of messages
            agent_filter: Optional agent name to filter assistant messages
            source_filter: Optional source/tab to filter messages
            
        Returns:
            List of messages
        """
        messages = self.messages
        
        if source_filter:
            filtered = []
            
            for i, msg in enumerate(messages):
                msg_source = msg.get('source')
                msg_agent = msg.get('agent')
                is_match = False
                
                # Check for direct source match
                if msg_source == source_filter:
                    is_match = True
                # If it's an assistant message, sometimes it only has the agent tag
                elif msg['role'] == 'assistant' and msg_agent == source_filter:
                    is_match = True
                # If it's a user message, check if the NEXT message is a matching assistant message
                elif msg['role'] == 'user' and i + 1 < len(messages):
                    next_msg = messages[i+1]
                    if next_msg.get('source') == source_filter or next_msg.get('agent') == source_filter:
                        is_match = True
                
                # Special logic for general chat
                if source_filter == 'chat' and not is_match:
                    # If it's not explicitly tagged as anything else, it's chat
                    specialist_agents = ['tax', 'portfolio', 'goal_planning', 'market', 'news']
                    if msg_agent not in specialist_agents and msg_source not in specialist_agents:
                        is_match = True
                
                if is_match:
                    # Fix crossover: if source_filter is market, strictly exclude portfolio agents
                    if source_filter == 'market' and msg_agent == 'portfolio':
                        is_match = False
                    
                    if is_match:
                        filtered.append(msg)
            
            messages = filtered

        # Secondary filter by agent if explicitly requested
        if agent_filter:
            agent_filtered = []
            for i, msg in enumerate(messages):
                if msg['role'] == 'assistant' and msg.get('agent') == agent_filter:
                    if i > 0 and messages[i-1]['role'] == 'user' and messages[i-1] not in agent_filtered:
                        agent_filtered.append(messages[i-1])
                    agent_filtered.append(msg)
            messages = agent_filtered
            
        if limit:
            return messages[-limit:]
        return messages
    
    def update_profile(self, updates: Dict[str, Any]):
        """
        Update user profile
        
        Args:
            updates: Dictionary of profile updates
        """
        self.user_profile.update(updates)
        self.last_accessed = datetime.now()
    
    def set_state(self, key: str, value: Any):
        """
        Set a state value
        
        Args:
            key: State key
            value: State value
        """
        self.state[key] = value
        self.last_accessed = datetime.now()
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """
        Get a state value
        
        Args:
            key: State key
            default: Default value if key not found
            
        Returns:
            State value
        """
        return self.state.get(key, default)
    
    def to_dict(self) -> Dict:
        """Convert session to dictionary for serialization"""
        return {
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat(),
            'messages': self.messages,
            'user_profile': self.user_profile,
            'portfolio': self.portfolio,
            'goals': self.goals,
            'state': self.state,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Session':
        """Create session from dictionary"""
        session = cls(session_id=data['session_id'])
        session.created_at = datetime.fromisoformat(data['created_at'])
        session.last_accessed = datetime.fromisoformat(data['last_accessed'])
        session.messages = data.get('messages', [])
        session.user_profile = data.get('user_profile', {})
        session.portfolio = data.get('portfolio', {})
        session.goals = data.get('goals', [])
        session.state = data.get('state', {})
        return session

    def add_goal(self, goal: Dict[str, Any]):
        """Add or update a goal"""
        if not self.goals:
            self.goals = []
        
        goal_exists = False
        for i, g in enumerate(self.goals):
            if g.get('name') == goal.get('name'):
                self.goals[i] = goal
                goal_exists = True
                break
        
        if not goal_exists:
            self.goals.append(goal)
        self.last_accessed = datetime.now()

    def set_portfolio(self, portfolio: Dict[str, Any]):
        """Set portfolio data"""
        self.portfolio = portfolio
        self.last_accessed = datetime.now()

class SessionManager:
    """Manages user sessions (Singleton)"""
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SessionManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config_path: str = "config.yaml"):
        if self._initialized:
            return
            
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.config = config['session']
        self.storage_type = self.config.get('storage', 'file')
        self.expiry_seconds = self.config.get('expiry', 86400)
        
        if self.storage_type == 'file':
            self.storage_path = Path(self.config.get('storage_path', 'data/sessions'))
            self.storage_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Initialized SessionManager with file storage at {self.storage_path}")
        else:
            logger.info(f"Initialized SessionManager with {self.storage_type} storage (in-memory)")
        
        self.sessions: Dict[str, Session] = {}
        self._initialized = True
    
    def create_session(self, session_id: str = None) -> Session:
        """
        Create a new session
        
        Args:
            session_id: Optional session ID to use
            
        Returns:
            New Session instance
        """
        session = Session(session_id=session_id)
        self.sessions[session.session_id] = session
        logger.info(f"Created new session: {session.session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get an existing session
        
        Args:
            session_id: Session ID
            
        Returns:
            Session instance or None if not found/expired
        """
        # Try in-memory first
        if session_id in self.sessions:
            session = self.sessions[session_id]
            if not self._is_expired(session):
                return session
            else:
                logger.debug(f"Session expired: {session_id}")
                del self.sessions[session_id]
                return None
        
        # Try loading from backend
        session = self._load_session(session_id)
        if session and not self._is_expired(session):
            self.sessions[session_id] = session
            return session
        
        return None
    
    def save_session(self, session: Session):
        """
        Save session to storage
        
        Args:
            session: Session to save
        """
        if self.storage_type == 'file':
            self._save_session_file(session)
    
    def _save_session_file(self, session: Session):
        """Save session to file"""
        try:
            session_file = self.storage_path / f"{session.session_id}.json"
            with open(session_file, 'w') as f:
                json.dump(session.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving session file {session.session_id}: {e}")

    def _load_session(self, session_id: str) -> Optional[Session]:
        """Load session from storage"""
        if self.storage_type == 'file':
            session_file = self.storage_path / f"{session_id}.json"
            if not session_file.exists():
                return None
            try:
                with open(session_file, 'r') as f:
                    data = json.load(f)
                return Session.from_dict(data)
            except Exception as e:
                logger.error(f"Error loading session file {session_id}: {e}")
        
        return None

    def delete_session(self, session_id: str):
        """
        Delete a session
        
        Args:
            session_id: Session ID to delete
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
        
        if self.storage_type == 'file':
            session_file = self.storage_path / f"{session_id}.json"
            if session_file.exists():
                session_file.unlink()
        
        logger.info(f"Deleted session: {session_id}")
    
    def _is_expired(self, session: Session) -> bool:
        """Check if session is expired"""
        age = datetime.now() - session.last_accessed
        return age.total_seconds() > self.expiry_seconds
