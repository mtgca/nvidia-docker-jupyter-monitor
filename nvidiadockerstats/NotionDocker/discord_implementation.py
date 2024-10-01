import requests
from dotenv import load_dotenv
import os

load_dotenv()

def send_discord_message(message):
    """Sends a message to a Discord webhook.

    Args:
        webhook_url (str): The URL of the Discord webhook.
        message (str): The message to send.
    """
    webhook_url = os.getenv("webhook_url")

    payload = {
        "content": message
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(webhook_url, json=payload, headers=headers)

    if response.status_code == 204:
        print("Message sent successfully!")
    else:
        print(f"Error sending message: {response.status_code}")

# Example usage:
if __name__ == '__main__':
    message = "haber las menciones <@&1264331652398841973>"
    send_discord_message(message)