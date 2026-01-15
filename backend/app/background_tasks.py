"""Background task management for async operations like description cleaning."""

import logging
import os
from uuid import UUID
from typing import Optional
import requests
from requests import RequestException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import crud
from app.validators import sanitize_api_key

logger = logging.getLogger(__name__)


def clean_description_with_ai(report_id: UUID, original_description: str):
    """
    Clean and improve the report description using AI.
    This runs in the background without blocking the user.
    
    Args:
        report_id: UUID of the report to update
        original_description: Original description text to improve
    """
    try:
        api_key = os.environ.get("BACKBOARD_API_KEY")
        if not api_key:
            logger.warning(f"Cannot clean description for report {report_id}: BACKBOARD_API_KEY not set")
            return
        
        # Create a new database session for this background task
        db = SessionLocal()
        try:
            report = crud.get_report(db, report_id)
            if not report:
                logger.warning(f"Report {report_id} not found for description cleaning")
                return
            
            # Call AI to clean the description
            cleaned_description = _call_ai_to_clean_description(api_key, original_description)
            
            if cleaned_description and cleaned_description != original_description:
                logger.info(f"Updating report {report_id} with cleaned description")
                crud.update_report(
                    db=db,
                    report_id=report_id,
                    new_description=cleaned_description
                )
            else:
                logger.info(f"No improvement made to description for report {report_id}")
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error cleaning description for report {report_id}: {e}", exc_info=True)


def _call_ai_to_clean_description(api_key: str, description: str) -> Optional[str]:
    """
    Call AI API to improve and clean the description text.
    
    Args:
        api_key: Backboard API key
        description: Original description to clean
    
    Returns:
        Cleaned/improved description, or None if AI call fails
    """
    try:
        # Create a simple message asking the AI to improve the description
        prompt = f"""Please improve and clarify the following civic report description. 
Make it more professional, clear, and concise while preserving all important details:

{description}

Return ONLY the improved description without any preamble."""
        
        # For now, we'll use a simple API call pattern
        # In production, you might want to use OpenAI API directly or another service
        backboard_url = "https://app.backboard.io/api/threads"
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key
        }
        
        # Create a thread for the cleaning task
        resp = requests.post(
            backboard_url,
            headers=headers,
            json={},
            timeout=30
        )
        resp.raise_for_status()
        thread_data = resp.json()
        thread_id = thread_data.get("thread_id")
        
        if not thread_id:
            logger.error("Failed to create thread for description cleaning")
            return None
        
        # Send the description for cleaning
        message_url = f"{backboard_url}/{thread_id}/messages"
        resp = requests.post(
            message_url,
            headers={
                "X-API-Key": api_key
            },
            data={
                "content": prompt,
                "llm_provider": "openai",
                "model_name": "gpt-5",
                "stream": "false",
                "web_search": "off",
                "send_to_llm": "true",
            },
            timeout=30
        )
        resp.raise_for_status()
        
        # Poll for response
        import time
        for attempt in range(1, 6):  # Try up to 5 times
            time.sleep(1)
            resp = requests.get(message_url.replace("/messages", ""), headers=headers, timeout=30)
            resp.raise_for_status()
            thread_data = resp.json()
            messages = thread_data.get("messages", [])
            
            if messages:
                last_message = messages[-1]
                if last_message.get("role") == "assistant" and last_message.get("status") == "COMPLETED":
                    content = last_message.get("content")
                    if isinstance(content, str):
                        return content.strip()
                    elif isinstance(content, dict):
                        return str(content).strip()
        
        logger.warning("Timeout waiting for AI to clean description")
        return None
        
    except RequestException as e:
        logger.error(f"Error calling AI for description cleaning: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in description cleaning: {e}", exc_info=True)
        return None
