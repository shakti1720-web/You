import os
import re
import asyncio

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError

API_ID = int(os.environ["TG_API_ID"])
API_HASH = os.environ["TG_API_HASH"]
CHAT = os.environ["TG_CHAT"]
SESSION = os.environ["TG_SESSION"]

DRY_RUN = os.environ.get("DRY_RUN", "true").lower() == "true"


def replace_caption(text):
    lines = text.splitlines()
    changed = False

    for i, line in enumerate(lines):
        if line.strip().lower().startswith("dm:-"):
            new_line = re.sub(
                r"(?i)@mranuj7(?!\w)",
                "@Shakti9992",
                line
            )

            if new_line != line:
                lines[i] = new_line
                changed = True

    return "\n".join(lines), changed


async def main():
    client = TelegramClient(
        StringSession(SESSION),
        API_ID,
        API_HASH
    )

    await client.connect()

    if not await client.is_user_authorized():
        raise RuntimeError(
            "TG_SESSION is invalid or expired."
        )

    print("Telegram login successful.")
    print(f"Chat: {CHAT}")
    print(f"DRY_RUN: {DRY_RUN}")

    found = 0
    edited = 0

    async for message in client.iter_messages(CHAT, reverse=True):
        if not message.message:
            continue

        new_text, changed = replace_caption(message.message)

        if not changed:
            continue

        found += 1
        print(f"Match: message {message.id}")

        if DRY_RUN:
            print("DRY RUN - not editing")
            continue

        try:
            await message.edit(new_text)
            edited += 1
            print(f"Edited: message {message.id}")
            await asyncio.sleep(1)

        except FloodWaitError as e:
            print(f"Flood wait: {e.seconds} seconds")
            await asyncio.sleep(e.seconds)

            await message.edit(new_text)
            edited += 1

    print(f"Matches found: {found}")
    print(f"Messages edited: {edited}")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
