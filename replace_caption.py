import asyncio
import os
from telethon import TelegramClient
from telethon.errors import FloodWaitError

API_ID = int(os.environ["TG_API_ID"])
API_HASH = os.environ["TG_API_HASH"]
CHAT = os.environ["TG_CHAT"]

OLD_TEXT = "@MRANUJ7"
NEW_TEXT = "@shakti9992"

# Only replace the exact "Extracted By:" line.
# Example:
# Extracted By: @MRANUJ7
# becomes:
# Extracted By: @shakti9992
DRY_RUN = os.environ.get("DRY_RUN", "true").lower() == "true"

SESSION = "telegram_session"

client = TelegramClient(SESSION, API_ID, API_HASH)


def replace_caption(text: str) -> str:
    lines = text.splitlines()
    changed = False
    output = []

    for line in lines:
        if line.strip().lower().startswith("extracted by:"):
            prefix, _, value = line.partition(":")
            if OLD_TEXT in value:
                line = f"{prefix}: {value.replace(OLD_TEXT, NEW_TEXT)}"
                changed = True
        output.append(line)

    return "\n".join(output) if changed else text


async def main():
    await client.start()
    print("Connected to Telegram.")

    edited = 0
    checked = 0

    async for message in client.iter_messages(CHAT, reverse=True):
        checked += 1

        if not message.message:
            continue

        new_caption = replace_caption(message.message)

        if new_caption == message.message:
            continue

        print(f"Message {message.id}: match found.")

        if DRY_RUN:
            print("DRY_RUN=true -> not editing.")
            continue

        try:
            await message.edit(new_caption)
            edited += 1
            print(f"Edited message {message.id}.")
            await asyncio.sleep(1)

        except FloodWaitError as e:
            print(f"Telegram requested a wait of {e.seconds} seconds.")
            await asyncio.sleep(e.seconds + 2)
            try:
                await message.edit(new_caption)
                edited += 1
                print(f"Edited message {message.id} after waiting.")
            except Exception as retry_error:
                print(f"Retry failed for {message.id}: {retry_error}")

        except Exception as e:
            print(f"Error on message {message.id}: {e}")
            await asyncio.sleep(3)

    print(f"Finished. Checked: {checked}, Edited: {edited}")


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
