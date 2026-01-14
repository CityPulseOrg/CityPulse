'''
This file is meant to be a script that creates the Backboard AI assistant, which
will become the brain of the CityPulse application.
'''

import os
from typing import Optional
import requests
from requests import RequestException
import logging
logger = logging.getLogger(__name__)
from app.validators import sanitize_api_key
from app.schemas import ClassificationEnum, SeverityEnum, PriorityEnum

#TODO: Make sure that timeout= can be used inside the API call
def create_assistant():
    api_key = os.environ.get("BACKBOARD_API_KEY")
    if not api_key:
        logger.error("BACKBOARD_API_KEY env variable not found or not set")
        return None

    existing_id = os.environ.get("ASSISTANT_ID")
    if existing_id:
        logger.info("ASSISTANT_ID already set; reusing existing assistant")
        return existing_id

    assistant_id = _find_existing_assistant_id(api_key=api_key, name="CPAssistant")
    if assistant_id:
        logger.info("Found existing assistant 'CPAssistant'; reusing")
        logger.info("Assistant ID: " + assistant_id)
        os.environ["ASSISTANT_ID"] = assistant_id
        logger.info("ASSISTANT_ID=%s", assistant_id)
        return assistant_id

    resp = None
    try:
        resp = requests.post("https://app.backboard.io/api/assistants",
                      headers={
                          "Content-Type": "application/json",
                          "X-API-Key": api_key
                      },
                      json={
                          "name": "CPAssistant",
                          "description": ("Analyzes civic issues reported by citizens and defines report "
                                          "field for usage by city staff"),
                          "tools": [
                              {
                                  "type": "function",
                                  "function": {
                                      "name": "analyze_report",
                                      "description": ("Construct the finalized report object with all the necessary fields "
                                                      "before it gets added to the database"),
                                      "parameters": {
                                          "type": "object",
                                          "properties": {
                                              "classification": {
                                                  "type": "string",
                                                  "description": "Category of the issue reported by the user",
                                                  "enum": [e.value for e in ClassificationEnum],
                                              },
                                              "severity": {
                                                  "type": "string",
                                                  "description": "Level of severity of the issue reported by the user",
                                                  "enum": [e.value for e in SeverityEnum],
                                              },
                                              "priority": {
                                                  "type": "string",
                                                  "description": ("Level of urgency of the issue reported by the user "
                                                                  "(i.e how quickly the report should be addressed)"),
                                                  "enum": [e.value for e in PriorityEnum],
                                              },
                                              "priority_score": {
                                                  "type": "number",
                                                  "description": ("A number between 0 and 100 representing the level "
                                                                  "of priority of the report (greater score means that "
                                                                  "it is more urgent and has greater priority)"),
                                              },
                                              "needs_clarification": {
                                                "type": "boolean",
                                                "description": ("True if the information given by the user is not clear "
                                                                "or not enough (ex: image blurred, scarce description)"),
                                              },
                                              "clarification": {
                                                  "type": "string",
                                                  "description": ("If needs_clarification is True, ask a simple question "
                                                                  "or multiple simple questions to clarify"),
                                              }
                                          },
                                          "required": [
                                              "classification",
                                              "severity",
                                              "priority",
                                              "priority_score",
                                              "needs_clarification",
                                          ],
                                          "if": {
                                              "properties": {
                                                  "needs_clarification": {"const": True},
                                              },
                                              "required": ["needs_clarification"],
                                          },
                                          "then": {
                                              "required": ["clarification"],
                                          },
                                      }
                                  }
                              }
                          ],
                          "embedding_provider": "openai",
                          "embedding_model_name": "text-embedding-3-large",
                          "embedding_dims": 3072
                      },
                      timeout=30
                      )
        resp.raise_for_status()
    except RequestException as e:
        error_msg = f"Error creating the assistant: {e}"
        if resp is not None:
            error_msg += f" | Response: {sanitize_api_key(resp.text, api_key)}"
        logger.error(error_msg)
        return None

    try:
        resp_json = resp.json()
    except ValueError as e:
        logger.error(f"Error parsing assistant creation response as JSON: {e} | Response: {sanitize_api_key(resp.text, api_key)}")
        return None

    logger.info("CPAssistant created successfully")
    assistant_id = resp_json.get("assistant_id")
    if assistant_id:
        logger.info("Assistant ID: " + assistant_id)
        os.environ["ASSISTANT_ID"] = assistant_id
        logger.info("ASSISTANT_ID=%s", assistant_id)
    return assistant_id


def _find_existing_assistant_id(api_key: str, name: str) -> Optional[str]:
    resp = None
    try:
        resp = requests.get(
            "https://app.backboard.io/api/assistants",
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key,
            },
            timeout=30,
        )
        resp.raise_for_status()
    except RequestException as e:
        error_msg = f"Error listing assistants: {e}"
        if resp is not None:
            error_msg += f" | Response: {sanitize_api_key(resp.text, api_key)}"
        logger.error(error_msg)
        return None

    try:
        payload = resp.json()
    except ValueError as e:
        logger.error(
            f"Error parsing assistant list response as JSON: {e} | Response: {sanitize_api_key(resp.text, api_key)}"
        )
        return None

    if isinstance(payload, list):
        assistants = payload
    elif isinstance(payload, dict):
        assistants = payload.get("assistants") or payload.get("data") or payload.get("items") or []
    else:
        assistants = []

    for item in assistants:
        if not isinstance(item, dict):
            continue
        if item.get("name") != name:
            continue
        assistant_id = item.get("assistant_id") or item.get("id")
        if assistant_id:
            return str(assistant_id)

    return None

if __name__ == "__main__":
    create_assistant()
