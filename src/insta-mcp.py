from fastmcp import FastMCP
from logger import logger
from instagrapi import Client
from dotenv import load_dotenv
from pathlib import Path
import os
import argparse
import json

load_dotenv()

INSTRUCTIONS = """
You are an Instagram Direct Message assistant. Your task is to help users manage and respond to their Instagram DMs effectively. 
Use the Instagram API to read and send messages as needed. Always ensure to respect user privacy and data security.
"""

client = Client()

def get_credentials():
    """Get Instagram credentials from CLI args or environment variables."""
    parser = argparse.ArgumentParser(description="Instagram MCP Credentials")
    parser.add_argument("--username", type=str, help="Instagram username (or set via ENV)")
    parser.add_argument("--password", type=str, help="Instagram password (or set via ENV)")
    args, _ = parser.parse_known_args()

    username = args.username or os.getenv("INSTAGRAM_USERNAME")
    password = args.password or os.getenv("INSTAGRAM_PASSWORD")

    if not username or not password:
        logger.error("Instagram credentials are required. Provide via CLI args or environment variables.")
        exit(1)
    
    return username, password


def login_instagram(username: str, password: str, client: Client):
    """Login to Instagram with session persistence."""
    session_file = Path(f".{username}_session.json")

    if session_file.exists():
        logger.info(f"Loading existing session from {session_file}")
        client.load_settings(session_file)

    try:
        if not client.user_id:
            logger.info(f"Logging in to Instagram as {username}...")
            client.login(username, password)
            client.dump_settings(session_file)
            logger.info(f"Session saved to {session_file}")
    except Exception as e:
        logger.error(f"Failed to login to Instagram: {e}")
        raise e

def tool_response(response: dict) -> str:
    """Convert dict response to JSON string for MCP."""
    return json.dumps(response)

# === LOGIN BEFORE REGISTERING TOOLS ===
USERNAME, PASSWORD = get_credentials()
login_instagram(USERNAME, PASSWORD, client)

# === MCP SETUP ===
mcp = FastMCP(name="Instagram DM MCP", instructions=INSTRUCTIONS)

@mcp.tool
def send_message(recipient_username: str, message: str) -> str:
    """Send an Instagram direct message to a user by username.

    Args:
        username: Instagram username of the recipient.
        message: The message text to send.
    Returns:
        A dictionary with success status and a status message.

    """

    if not recipient_username or not message:
        return tool_response({"success": False, "error": "Recipient username and message cannot be empty."})

    try:
        user_id = client.user_id_from_username(recipient_username)
        if not user_id:
            return tool_response({"success": False, "error": f"User '{recipient_username}' not found."})
        
        direct_message = client.direct_send(message, [user_id])
        if direct_message:
            return tool_response({"success": True, "message": "Message sent to user.", "direct_message_id": getattr(direct_message, 'id', None)})
        else:
            return tool_response({"success": False, "message": "Failed to send message."})
    except Exception as e:
        logger.error(f"Failed to send message to {recipient_username}: {e}")
        return tool_response({"success": False, "error": str(e)})

if __name__ == "__main__":
    logger.info("Starting MCP server...")
    mcp.run(transport="stdio")