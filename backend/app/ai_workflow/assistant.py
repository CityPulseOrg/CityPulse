'''
This file is meant to be a script that creates the Backboard AI assistant, which
will become the brain of the CityPulse application.
'''

import os
import json
import requests

def create_assistant():
    response = requests.post("https://app.backboard.io/api/assistants",
                  headers={
                      "Content-Type": "application/json",
                      "X-API-Key": os.environ.get("BACKBOARD_API_KEY")
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
                                          "classification", "severity", "priority", "priority_score", "clarification"
                                      ]
                                  }
                              }
                          }
                      ],
                      "embedding_provider": "openai",
                      "embedding_model_name": "text-embedding-3-large",
                      "embedding_dims": 3072
                  }
                  )

    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        print("Sorry, there was an error creating the assistant: ")
        print(response.text)
        return

    response = response.json()
    print("CPAssistant created successfully")
    assistantId = response.get("assistant_id")
    if assistantId:
        print("Assistant ID: " + assistantId)

