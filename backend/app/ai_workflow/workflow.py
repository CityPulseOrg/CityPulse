'''
This file encompasses multiple functions to interact with the Backboard.io API and perform operations such as
creating threads for individual reports and adding issue images to existing threads.
'''

import os
import json
import requests
from requests import RequestException
import logging
logger = logging.getLogger(__name__)
from typing import List
from fastapi import UploadFile

#TODO: add polling if necessary
#TODO: Get Assistant ID and put it in the backboard url
def create_thread(assistantId: str, api_key: str):
    response = requests.post(
        f"https://app.backboard.io/api/assistants/{assistantId}/threads",
        headers={
            "Content-Type": "application/json",
            "X-API-Key": api_key
        },
        json={},
        timeout=30
    )

    try:
        response.raise_for_status()
    except requests.HTTPError:
        logger.error("Sorry, there was an error creating the thread")
        return None, None

    try:
        response = response.json()
    except ValueError:
        logger.error("Sorry, the thread create returned non-JSON")
        return None, None

    threadId = response.get("thread_id")
    creationTime = response.get("created_at")
    if not threadId:
        print(f"Could not find thread ID in response: {response}")
        return None, None
    if not creationTime:
        print(f"Could not find creation time in response: {response}")
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

    response = requests.post(backboardUrl, headers = headers, data = data, files = imagesArray, timeout=30)
    try:
        response.raise_for_status()
        return response
    except requests.HTTPError as e:
        print("Sorry, there was an error uploading the message: ")
        print(response.text)
        return None

#TODO: Make sure that the timeout= is necessary in the API call
def get_assistant_response(api_key: str, threadId: str):
    try:
        thread = requests.get(
            f"https://app.backboard.io/api/threads/{threadId}",
            headers={
                "X-API-Key": api_key
            },
            timeout=30
        )
        thread.raise_for_status()
    except requests.HTTPError:
        print("Sorry, there was an error getting the thread: ")
        print(thread.text)
        return {}

    try:
        thread = thread.json()
    except ValueError:
        logger.error("Sorry, there was a json error when getting the thread")
        return {}

    messages = thread.get("messages")
    if not messages:
        return {}
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

    return {}

def run_backboard_ai(description: str, imageFiles: List[UploadFile]):
    api_key = os.environ.get("BACKBOARD_API_KEY")
    assistant_id = os.environ.get("ASSISTANT_ID")
    if not api_key or not assistant_id:
        logger.error("BACKBOARD_API_KEY or ASSISTANT_ID not found or could not be retrieved")
        return None, None, {}

    try:
        thread = create_thread(assistant_id, api_key)
        threadId, creationTime = thread
        if threadId is None or creationTime is None:
            return None, None, {}

        uploaded_data = upload_information_to_thread(api_key, threadId, description, imageFiles)
        if uploaded_data is None:
            return None, None, {}

        response = get_assistant_response(api_key, threadId)
        return threadId, creationTime, response
    except RequestException:
        logger.error("Sorry, there was a request failure (timeout or connection error)")
        return None, None, {}


