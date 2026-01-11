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
def create_thread(assistant_id: str, api_key: str):
    resp = None
    try:
        resp = requests.post(
            f"https://app.backboard.io/api/assistants/{assistant_id}/threads",
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key
            },
            json={},
            timeout=30
        )
        resp.raise_for_status()
    except RequestException as e:
        response_text = sanitize_api_key(resp.text, api_key) if resp is not None else None
        logger.exception("Error creating the thread: %s | Response: %s", e, response_text)
        return None, None

    try:
        resp_json = resp.json()
    except ValueError as e:
        logger.exception(
            "Thread create returned non-JSON: %s | Response: %s",
            e,
            sanitize_api_key(resp.text, api_key),
        )
        return None, None

    thread_id = resp_json.get("thread_id")
    creation_time = resp_json.get("created_at")
    if not thread_id:
        logger.error("Could not find thread ID in response")
        return None, None
    if not creation_time:
        logger.error("Could not find creation time in response")
        return None, None
    return thread_id, creation_time

# TODO: Make sure that Content-Type does not need to be defined and verify if requests lib will automatically set it
# TODO: Need to finish the last part of the function
def upload_information_to_thread(api_key: str, thread_id: str, description: str, image_files: List[UploadFile]):
    backboard_url = f"https://app.backboard.io/api/threads/{thread_id}/messages"
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

    images_array = []
    for file in image_files:
        filename = file.filename or "image.jpg"
        mimetype = getattr(file, "content_type", "image/jpeg")
        file_object = file.file
        images_array.append(("files", (filename, file_object, mimetype)))

    resp = None
    try:
        resp = requests.post(backboard_url, headers=headers, data=data, files=images_array, timeout=30)
        resp.raise_for_status()
        return resp
    except RequestException as e:
        error_msg = f"Error uploading the message: {e}"
        if resp is not None:
            error_msg += f" | Response: {sanitize_api_key(resp.text, api_key)}"
        logger.error(error_msg)
        return None

#TODO: Make sure that the timeout= is necessary in the API call
def get_assistant_response(api_key: str, thread_id: str, max_attempts: int = 8, base_delay: float = 0.5):
    backboard_url = f"https://app.backboard.io/api/threads/{thread_id}"
    headers = {"X-API-Key": api_key}
    timeout = 30

    for attempt in range(1, max_attempts + 1):
        resp = None
        try:
            resp = requests.get(url=backboard_url, headers=headers, timeout=timeout)
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
            last_message = messages[- 1]
            if last_message.get("role") == "assistant" and last_message.get("status") == "COMPLETED":
                content = last_message.get("content")
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
            if last_message.get("status") in {"FAILED", "CANCELLED", "ERROR"}:
                logger.error("Sorry, the assistant message on thread was not retrieved")
                return {}
        
        if attempt < max_attempts:
            logger.info(f"Assistant did not respond on the given thread. Waiting {base_delay} before retrying")
            time.sleep(base_delay)
            base_delay *= 2
        else:
            logger.info(f"Maximum amount of attempts reached while waiting for the assistant response on thread {thread_id}")

    return {}

def run_backboard_ai(description: str, image_files: List[UploadFile]):
    api_key = os.environ.get("BACKBOARD_API_KEY")
    assistant_id = os.environ.get("ASSISTANT_ID")
    if not api_key or not assistant_id:
        logger.error("BACKBOARD_API_KEY or ASSISTANT_ID not found or could not be retrieved")
        return None, None, {}

    try:
        thread_id, creation_time = create_thread(assistant_id, api_key)
        if thread_id is None or creation_time is None:
            return None, None, {}

        uploaded_data = upload_information_to_thread(api_key, thread_id, description, image_files)
        if uploaded_data is None:
            return None, None, {}

        ai_response = get_assistant_response(api_key, thread_id)
        return thread_id, creation_time, ai_response
    except RequestException as e:
        logger.error(f"Request failure in AI workflow: {e}")
        return None, None, {}


