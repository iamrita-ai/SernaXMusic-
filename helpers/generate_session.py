"""
Run this ONCE, locally, on your own machine (not on Render) to generate
a Pyrogram STRING_SESSION for the assistant account that will join
group Voice Chats.

    python helpers/generate_session.py

You'll be asked for API_ID, API_HASH (from https://my.telegram.org)
and then to log in with the phone number of the account you want to
use as the VC assistant (NOT the bot itself — a normal user account).
The resulting string goes into STRING_SESSION in your .env / Render
environment.
"""

from pyrogram import Client

api_id = int(input("API_ID: "))
api_hash = input("API_HASH: ")

with Client("session_gen", api_id=api_id, api_hash=api_hash, in_memory=True) as app:
    print("\n✅ Your STRING_SESSION:\n")
    print(app.export_session_string())
    print("\nPaste this into STRING_SESSION in your .env / Render env vars.\n")
