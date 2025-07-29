import requests
import json
import argparse
import os

def send_webex_message(bot_token, room_id, markdown_message, fallback_text="Webex client does not support markdown."):
    """
    Sends a message to a Webex room using bot token and markdown content.

    Args:
        bot_token (str): Webex bot token
        room_id (str): Webex room ID to send message to
        markdown_message (str): Message in markdown format
        fallback_text (str): Plain text fallback for clients that don't support markdown

    Returns:
        dict: Response JSON from Webex API
    """
    url = "https://webexapis.com/v1/messages"

    payload = json.dumps({
        "roomId": room_id,
        "markdown": markdown_message,
        "text": fallback_text
    })
    headers = {
        'Authorization': f'Bearer {bot_token}',
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, data=payload)
    try:
        return response.json()
    except Exception:
        return {"error": "Invalid JSON response", "status_code": response.status_code, "body": response.text}

def send_webex_file_message(bot_token, room_id, message_text, file_path, file_type="text/plain"):
    """
    Sends a message with a file attachment to a Webex room.

    Parameters:
        token (str): Webex Bot access token.
        room_id (str): Webex room ID.
        message_text (str): The message text.
        file_path (str): Path to the file to be attached.
        file_type (str): MIME type of the file (default is 'text/plain').

    Returns:
        Response text from the Webex API.
    """
    url = "https://webexapis.com/v1/messages"
    headers = {
        'Authorization': f'Bearer {bot_token}'
    }

    payload = {
        'roomId': room_id,
        'text': message_text
    }

    with open(file_path, 'rb') as file_data:
        files = [('files', (file_path, file_data, file_type))]
        response = requests.post(url, headers=headers, data=payload, files=files)

    return response.text

if __name__ == "__main__":
    bot_token = os.getenv("BOT_TOKEN")
    room_id = os.getenv("ROOM_ID")
    
    parser = argparse.ArgumentParser(description="Send a Webex Teams message with markdown content.")
    parser.add_argument('-r', '--router', required=True, help='Router that has the issue')
 
    args = parser.parse_args()

    message = f"""
# SR-DPM Alert!
An Error was detected on router **{(args.router).upper()}** by Splunk indicating an SR-DPM failure
## Router Diagnostics
```
show mpls oam dpm prefix
show mpls oam dpm prefix fault
```
"""

    response = send_webex_message(
        bot_token,
        room_id,
        markdown_message=message,
    )

    print(json.dumps(response, indent=2))