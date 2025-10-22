"""
Helper script to set up Instagram credentials in a .env file.
"""

import os
import getpass


def setup_env():
    """Interactive setup for Instagram credentials."""
    print("\n📱 Instagram DM MCP - Environment Setup")
    print("=" * 40, "\n")

    env_path = ".env"

    # Check for existing .env file
    if os.path.exists(env_path):
        overwrite = input(f"{env_path} already exists. Overwrite? (y/n): ").strip().lower()
        if overwrite != "y":
            print("⚠️  Setup aborted. Existing .env file not modified.")
            return

    # Collect credentials
    username = input("👤 Enter your Instagram username: ").strip()
    password = getpass.getpass("🔑 Enter your Instagram password: ").strip()

    if not username or not password:
        print("❌ Username and password are required!")
        return

    # Prepare .env content
    env_content = (
        "# Instagram Credentials\n"
        f"INSTAGRAM_USERNAME={username}\n"
        f"INSTAGRAM_PASSWORD={password}\n"
    )

    # Write to file
    try:
        with open(env_path, "w", encoding="utf-8") as file:
            file.write(env_content)
        print("\n✅ .env file created successfully!")
        print("🔒 Your credentials are now stored securely in the .env file.\n")
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")


if __name__ == "__main__":
    setup_env()