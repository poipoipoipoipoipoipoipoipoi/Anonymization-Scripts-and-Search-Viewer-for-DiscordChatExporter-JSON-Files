import os
import json

# CONFIG — Set this to your cleaned folder
FOLDER_PATH = r"Your\Path\Here"
OUTPUT_FILE = os.path.join(FOLDER_PATH, "merged_filtered_messages.json")

TARGET_NAME = "XXX"
TARGET_DISC = "XXXX"

# Step 1: Load all messages and collect lookup info
all_messages = []
author_lookup = {}  # message_id → {name, discriminator}

for filename in os.listdir(FOLDER_PATH):
    if not filename.endswith(".json"):
        continue

    path = os.path.join(FOLDER_PATH, filename)

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict) or "messages" not in data:
            continue

        for msg in data["messages"]:
            msg_id = msg.get("id")
            author = msg.get("author") or {}
            if msg_id:
                author_lookup[msg_id] = {
                    "name": author.get("name"),
                    "discriminator": author.get("discriminator"),
                }
            all_messages.append(msg)

    except Exception as e:
        print(f"⚠️ Error loading {filename}: {e}")

# Step 2: Filter and transform valid messages
filtered_messages = []

for msg in all_messages:
    author = msg.get("author", {})

    if author.get("name") != TARGET_NAME or author.get("discriminator") != TARGET_DISC:
        continue

    # Redact mention names + remove discriminators
    for mention in msg.get("mentions", []):
        mention["name"] = "NAME_REDACTED"
        mention.pop("discriminator", None)

    for reaction in msg.get("reactions", []):
        for user in reaction.get("users", []):
            user["name"] = "NAME_REDACTED"
            user.pop("discriminator", None)

    # Handle reference logic
    if "reference" in msg:
        ref = msg["reference"]
        ref_id = ref.get("messageId")

        if not ref_id or ref_id not in author_lookup:
            msg["reference"] = "REPLIED_MESSAGE_NOT_FOUND"
        else:
            ref_author = author_lookup[ref_id]
            if ref_author.get("name") == TARGET_NAME and ref_author.get("discriminator") == TARGET_DISC:
                msg["reference"] = "FOLLOW-UP"
            else:
                msg["reference"] = "REPLIED_MESSAGE_REDACTED"

    # Remove discriminator from author
    author.pop("discriminator", None)

    # Keep everything else (no field deletion unless instructed)
    filtered_messages.append(msg)

# Step 3: Write final merged JSON
output = {
    "messages": filtered_messages
}

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"✅ Done. Filtered messages saved to:\n{OUTPUT_FILE}")
