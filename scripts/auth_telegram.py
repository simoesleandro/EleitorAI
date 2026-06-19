"""One-time Telegram authentication via Telethon.

Run this ONCE in an interactive terminal (NOT as a daemon) to:
1. Create a session file `eleitorai_session.session`
2. Cache the auth key so future daemon calls don't need stdin

Usage:
    .venv\Scripts\python.exe scripts/auth_telegram.py

You'll be prompted for your phone number (international format: +55...)
and a code sent to your Telegram app.
"""
import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

API_ID = os.environ.get("TELEGRAM_API_ID")
API_HASH = os.environ.get("TELEGRAM_API_HASH")

if not API_ID or not API_HASH:
    print("ERROR: TELEGRAM_API_ID and TELEGRAM_API_HASH must be set in .env", file=sys.stderr)
    sys.exit(1)

SESSION_PATH = Path(__file__).resolve().parent.parent / "eleitorai_session"


async def main():
    client = TelegramClient(str(SESSION_PATH), int(API_ID), API_HASH)
    print(f"Session path: {SESSION_PATH}.session")
    print("Connecting to Telegram...")
    await client.start()
    me = await client.get_me()
    print(f"Authenticated as: {me.first_name} {me.last_name or ''} (@{me.username or 'no-username'})")
    print(f"Phone: {me.phone}")
    print(f"Session file created. Future calls will use this session (no interactive prompt).")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
