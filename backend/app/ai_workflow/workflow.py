'''
This file encompasses multiple functions to interact with the Backboard.io API and perform operations such as
creating threads for individual reports and adding issue images to existing threads.
'''

import os
import json
import requests
from typing import List
from fastapi import UploadFile

#TODO: Get Assistant ID and put it in the backboard url
def create_thread(assistantId: str):
    response = requests.post(
        f"https://app.backboard.io/api/assistants/{assistantId}/threads",
        headers={
            "Content-Type": "application/json",
            "X-API-Key": os.environ.get("BACKBOARD_API_KEY")
        },
        json={},
        timeout=30
    )

    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        print("Sorry, there was an error creating the thread: ")
        print(response.text)
        return None, None

    response = response.json()
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
def upload_information_to_thread(threadId: str, description: str, imageFiles: List[UploadFile]):
    backboardUrl = f"https://app.backboard.io/api/threads/{threadId}/messages"
    headers = {
            # "Content-Type": "multipart/form-data",
            "X-API-Key": os.environ.get("BACKBOARD_API_KEY")
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
def get_assistant_response(threadId: str):
    try:
        thread = requests.get(
            f"https://app.backboard.io/api/threads/{threadId}",
            headers={
                "X-API-Key": os.environ.get("BACKBOARD_API_KEY")
            },
            timeout=30
        )
        thread.raise_for_status()
    except requests.HTTPError:
        print("Sorry, there was an error getting the thread: ")
        print(thread.text)
        return {}

    thread = thread.json()
    messages = thread.get("messages")
    if not messages:
        return {}
    lastMessage = messages[- 1]
    if lastMessage.get("role") == "assistant" and lastMessage.get("status") == "COMPLETED":
        content = lastMessage.get("content")
        if isinstance(content, str):
            return json.loads(content)
        elif isinstance(content, dict):
            return content

    return {}

def run_backboard_ai(description: str, imageFiles: List[UploadFile]):
    thread = create_thread(os.environ.get("BACKBOARD_ID"))
    if not thread:
        return None, None, {}
    threadId, creationTime = thread
    uploaded_data = upload_information_to_thread(threadId, description, imageFiles)
    if uploaded_data == None:
        return None, None, {}
    response = get_assistant_response(threadId)
    return threadId, creationTime, response


