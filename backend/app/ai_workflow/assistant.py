'''
This file is meant to be a script that creates the Backboard AI assistant, which
will become the brain of the CityPulse application.
'''

import os
import requests
from requests import RequestException
import logging
logger = logging.getLogger(__name__)

#TODO: Make sure that timeout= can be used inside the API call
def create_assistant():
    api_key = os.environ.get("BACKBOARD_API_KEY")
    if not api_key:
        logger.error("BACKBOARD_API_KEY env variable not found or not set")
        return None

    try:
        response = requests.post("https://app.backboard.io/api/assistants",
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
                                                  "enum": [
                                                      "pothole",
                                                      "broken_streetlight",
                                                      "broken_street_sign",
                                                      "excessive_dumping",
                                                      "illegal_graffiti",
                                                      "vandalism",
                                                      "overgrown_grass",
                                                      "unplowed_area",
                                                      "icy_street",
                                                      "icy_sidewalk",
                                                      "malfunctioning_waterfountain",
                                                      "other"
                                                  ],
                                              },
                                              "severity": {
                                                  "type": "string",
                                                  "description": "Level of severity of the issue reported by the user",
                                                  "enum": [
                                                      "very_low",
                                                      "low",
                                                      "medium",
                                                      "high",
                                                      "very_high"
                                                  ],
                                              },
                                              "priority": {
                                                  "type": "string",
                                                  "description": ("Level of urgency of the issue reported by the user "
                                                                  "(i.e how quickly the report should be addressed)"),
                                                  "enum": [
                                                      "not_urgent",
                                                      "urgent",
                                                      "very_urgent"
                                                  ],
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
                                          ]
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
        response.raise_for_status()
    except RequestException:
        logger.exception("Sorry, there was an error creating the assistant")
        return None

    try:
        response_json = response.json()
    except ValueError:
        logger.exception("Sorry, there was an error parsing assistant creation response as JSON")
        return None

    logger.info("CPAssistant created successfully")
    assistantId = response_json.get("assistant_id")
    if assistantId:
        logger.info("Assistant ID: " + assistantId)
    return assistantId

#TODO: Verify if this line is needed
if __name__ == "__main__":
    create_assistant()
