'''
This file encompasses multiple functions to interact with the Backboard.io API and perform operations such as
creating threads for individual reports and adding issue images to existing threads.
'''

import os
import json
import requests
import time
from requests import RequestException
import logging
logger = logging.getLogger(__name__)
from typing import List, Any, Dict, Optional
from fastapi import UploadFile
from app.validators import sanitize_api_key

#TODO: add polling if necessary
#TODO: Get Assistant ID and put it in the backboard url
def create_thread(assistantId: str, api_key: str):
    resp = None
    try:
        resp = requests.post(
            f"https://app.backboard.io/api/assistants/{assistantId}/threads",
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key
            },
            json={},
            timeout=30
        )
        resp.raise_for_status()
    except RequestException as e:
        error_msg = f"Error creating the thread: {e}"
        if resp is not None:
            error_msg += f" | Response: {sanitize_api_key(resp.text, api_key)}"
        logger.error(error_msg)
        return None, None

    try:
        resp_json = resp.json()
    except ValueError as e:
        logger.error(f"Thread create returned non-JSON: {e} | Response: {sanitize_api_key(resp.text, api_key)}")
        return None, None

    threadId = resp_json.get("thread_id")
    creationTime = resp_json.get("created_at")
    if not threadId:
        logger.error(f"Could not find thread ID in response")
        return None, None
    if not creationTime:
        logger.error(f"Could not find creation time in response")
        return None, None
    return threadId, creationTime

# TODO: Make sure that Content-Type does not need to be defined and verify if requests lib will automatically set it
# TODO: Need to finish the last part of the function
def upload_information_to_thread(api_key: str, threadId: str, description: str, imageFiles: List[UploadFile]):
    backboardUrl = f"https://app.backboard.io/api/threads/{threadId}/messages"
    headers = {
            # "Content-Type": "multipart/form-data",
            "X-API-Key": api_key
        }
    data = {
            "content": description,
            "llm_provider": "openai",
            "model_name": "gpt-5",
            "stream": "false",
            "memory": "Auto",
            "web_search": "off",
            "send_to_llm": "true",
            "metadata": ""
        }

    imagesArray = []
    for file in imageFiles:
        filename = file.filename or "image.jpg"
        mimetype = getattr(file, "content_type", "image/jpeg")
        fileObject = file.file
        imagesArray.append(("files", (filename, fileObject, mimetype)))

    resp = None
    try:
        resp = requests.post(backboardUrl, headers=headers, data=data, files=imagesArray, timeout=30)
        resp.raise_for_status()
        return resp
    except RequestException as e:
        error_msg = f"Error uploading the message: {e}"
        if resp is not None:
            error_msg += f" | Response: {sanitize_api_key(resp.text, api_key)}"
        logger.error(error_msg)
        return None

#TODO: Make sure that the timeout= is necessary in the API call
def get_assistant_response(api_key: str, threadId: str, max_attempts: int = 8, base_delay: float = 0.5):
    url = f"https://app.backboard.io/api/threads/{threadId}"
    headers = {"X-API-Key": api_key}
    timeout = 30

    for attempt in range(1, max_attempts + 1):
        resp = None
        try:
            resp = requests.get(url=url, headers=headers, timeout=timeout)
            resp.raise_for_status()
        except RequestException as e:
            error_msg = f"Error getting the thread: {e}"
            if resp is not None:
                error_msg += f" | Response: {sanitize_api_key(resp.text, api_key)}"
            logger.error(error_msg)
            return {}

        try:
            resp_json = resp.json()
        except ValueError as e:
            logger.error(f"Error parsing thread response as JSON: {e} | Response: {sanitize_api_key(resp.text, api_key)}")
            return {}

        messages = resp_json.get("messages")
        if not messages:
            return {}
        else:
            lastMessage = messages[- 1]
            if lastMessage.get("role") == "assistant" and lastMessage.get("status") == "COMPLETED":
                content = lastMessage.get("content")
                if isinstance(content, str):
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        logger.error("Sorry, the json response from the assistant was invalid")
                        return {}
                elif isinstance(content, dict):
                    return content
                else:
                    logger.error("Sorry, we encountered an unexpected content type")
                    return {}
            if lastMessage.get("status") in {"FAILED", "CANCELLED", "ERROR"}:
                logger.error("Sorry, the assistant message on thread was not retrieved")
                return {}
        
        if attempt < max_attempts:
            logger.info(f"Assistant did not respond on the given thread. Waiting {base_delay} before retrying")
            time.sleep(base_delay)
            base_delay *= 2
        else:
            logger.info(f"Maximum amount of attempts reached while waiting for the assistant response on thread {threadId}")

    return {}

def run_backboard_ai(description: str, imageFiles: List[UploadFile]):
    api_key = os.environ.get("BACKBOARD_API_KEY")
    assistant_id = os.environ.get("ASSISTANT_ID")
    if not api_key or not assistant_id:
        logger.error("BACKBOARD_API_KEY or ASSISTANT_ID not found or could not be retrieved")
        return None, None, {}

    try:
        threadId, creationTime = create_thread(assistant_id, api_key)
        if threadId is None or creationTime is None:
            return None, None, {}

        uploaded_data = upload_information_to_thread(api_key, threadId, description, imageFiles)
        if uploaded_data is None:
            return None, None, {}

        ai_response = get_assistant_response(api_key, threadId)
        return threadId, creationTime, ai_response
    except RequestException as e:
        logger.error(f"Request failure in AI workflow: {e}")
        return None, None, {}


