import os
import requests
import difflib
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Set up your Slack API token
slack_token = "5880294174:AAHv-DvYuh8GV5-M2hxEaW0vcYwdmBc-TFc"
client = WebClient(token=slack_token)

# Define the channel ID of the main channel you want to parse
channel_id = id channel"

# Create a directory to save the messages and photos
output_dir = "slack_parser_output"
os.makedirs(output_dir, exist_ok=True)

# Function to save messages to a text file
def save_message(message, output_file):
    with open(output_file, "a") as file:
        file.write(f"{message['text']}\n")

def save_photo(file_id, output_file):
    try:
        response = client.files_info(file=file_id)
        url_private = response["file"]["url_private_download"]
        filename = response["file"]["name"]
        file_extension = os.path.splitext(filename)[1]
        file_name = f"{os.path.basename(output_file)}{file_extension}"  # Extract the filename from the output_file
        file_path = os.path.join(output_dir, file_name)

        # Check if the file already exists
        if os.path.exists(file_path):
            print(f"File already exists: {filename}")
            return

        # Download the file using the URL
        response = requests.get(url_private, headers={"Authorization": f"Bearer {slack_token}"})
        response.raise_for_status()

        with open(file_path, "wb") as file:
            file.write(response.content)

        print(f"Saved photo: {filename}")
    except SlackApiError as e:
        print(f"Error saving photo: {e.response['error']}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading photo: {str(e)}")

# Function to check if the file content is similar to the message text
def is_file_content_similar(file_path, message_text):
    try:
        with open(file_path, "r", encoding="ANSI") as file:
            file_content = file.read()
    except FileNotFoundError:
        # If the file doesn't exist, create an empty file
        with open(file_path, "w", encoding="ANSI") as file:
            file_content = ""

    similarity_ratio = difflib.SequenceMatcher(None, file_content, message_text).ratio()
    similarity_threshold = 0.9
    return similarity_ratio >= similarity_threshold


# Define the delay in seconds
delay_seconds = 10

# Infinite loop for continuous execution
while True:
    try:
        # Retrieve and save messages from the main channel
        response = client.conversations_history(channel=channel_id)
        messages = response["messages"]

        for index, message in enumerate(reversed(messages), start=1):
            if "subtype" in message:  # Ignore system messages and file uploads
                continue

            # Create a subdirectory for each message
            message_dir = output_dir
            os.makedirs(message_dir, exist_ok=True)

            # Check if the file content is similar to any previously saved message
            file_path = os.path.join(message_dir, f"{index}.txt")
            if is_file_content_similar(file_path, message["text"]):
                print(f"Skipping file: {file_path}")
                continue

            save_message(message, file_path)

            if "files" in message:  # Check for attached files (photos)
                for file_index, file in enumerate(message["files"], start=1):
                    file_name = f"{index}.{file_index}"
                    save_photo(file["id"], os.path.join(message_dir, file_name))

            if "reply_count" in message:  # Check if it's a thread (discussion)
                conversation_id = message["ts"]
                try:
                    response = client.conversations_replies(channel=channel_id, ts=conversation_id)
                    replies = response["messages"]

                    for reply_index, reply in enumerate(replies, start=1):
                        if "subtype" in reply:  # Ignore system messages and file uploads
                            continue

                        save_message(reply, os.path.join(message_dir, f"{index}.{reply_index}.txt"))

                        if "files" in reply:  # Check for attached files (photos)
                            for file_index, file in enumerate(reply["files"], start=1):
                                file_name = f"{index}.{reply_index}.{file_index}"
                                save_photo(file["id"], os.path.join(message_dir, file_name))
                except SlackApiError as e:
                    print(f"Error retrieving replies: {e.response['error']}")

        # Sleep for the specified delay
        time.sleep(delay_seconds)

    except SlackApiError as e:
        print(f"Error retrieving messages: {e.response['error']}")
        # You may choose to break the loop or handle the error in a different way

    except KeyboardInterrupt:
        # Break the loop if the user interrupts the program
        break
