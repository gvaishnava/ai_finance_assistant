"""
User profile endpoints
"""

from fastapi import APIRouter, HTTPException

from src.web_app.models import UserProfileUpdate
from src.core.session import SessionManager
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Initialize session manager
session_manager = SessionManager()

@router.get("/profile/{session_id}")
async def get_profile(session_id: str):
    """
    Get user profile
    
    Args:
        session_id: Session ID
        
    Returns:
        User profile data
    """
    try:
        session = session_manager.get_session(session_id)
        
        if not session:
             # Auto-create session if it doesn't exist (frontend generated ID)
             logger.info(f"Session {session_id} not found, creating new one")
             session = session_manager.create_session(session_id=session_id)
        
        return {"profile": session.user_profile}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/profile/{session_id}")
async def update_profile(session_id: str, updates: UserProfileUpdate):
    """
    Update user profile
    
    Args:
        session_id: Session ID
        updates: Profile updates
        
    Returns:
        Updated profile
    """
    try:
        session = session_manager.get_session(session_id)
        
        if not session:
             # Auto-create session if it doesn't exist
             logger.info(f"Session {session_id} not found, creating new one")
             session = session_manager.create_session(session_id=session_id)
        
        # Update profile
        update_dict = updates.dict(exclude_none=True)
        session.update_profile(update_dict)
        
        # Save session
        session_manager.save_session(session)
        
        return {"profile": session.user_profile}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}")
async def get_full_session(session_id: str):
    """
    Get full session state (profile, portfolio, goals)
    
    Args:
        session_id: Session ID
        
    Returns:
        Full session state
    """
    try:
        session = session_manager.get_session(session_id)
        
        if not session:
             # Auto-create if it doesn't exist
             logger.info(f"Session {session_id} not found, creating new one")
             session = session_manager.create_session(session_id=session_id)
        
        return {
            "session_id": session_id,
            "profile": session.user_profile,
            "portfolio": session.portfolio,
            "goals": session.goals,
            "last_accessed": session.last_accessed.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting full session: {e}")
        raise HTTPException(status_code=500, detail=str(e))
