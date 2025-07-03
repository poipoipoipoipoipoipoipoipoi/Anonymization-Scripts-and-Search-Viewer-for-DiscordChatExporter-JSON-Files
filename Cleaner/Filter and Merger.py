import os
import json

# Set your folder path here
FOLDER_PATH = r"Your\Path\Here"

# Fields to remove from message level
message_fields_to_remove = [
    "timestamp", "timestampEdited", "callEndedTimestamp", "isPinned"
]

# Fields to remove from author, mentions, and reactions.users[i]
user_fields_to_remove = [
    "id", "nickname", "color", "isBot", "roles", "avatarUrl"
]

# Fields to replace with placeholders if non-empty
content_replacements = {
    "attachments": "ATTACHMENT_REDACTED",
    "stickers": "STICKER_REDACTED",
    "embeds": "EMBED_REDACTED"
}

# Store logs here
log_lines = []

def clean_user_object(user_obj):
    for field in user_fields_to_remove:
        user_obj.pop(field, None)

def clean_message(msg):
    # Remove general metadata
    for field in message_fields_to_remove:
        msg.pop(field, None)

    # Replace content fields with placeholders if not empty
    for field, placeholder in content_replacements.items():
        if field in msg and msg[field]:
            msg[field] = placeholder
        else:
            msg[field] = []

    # Clean the author object
    if "author" in msg:
        clean_user_object(msg["author"])

    # Clean mentions
    if "mentions" in msg:
        for mention in msg["mentions"]:
            clean_user_object(mention)

    # Clean reactions[].users[]
    if "reactions" in msg:
        for reaction in msg["reactions"]:
            if "users" in reaction:
                for user in reaction["users"]:
                    clean_user_object(user)

    return msg

def process_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        log_lines.append(f"❌ Error decoding {file_path}: {e}")
        return
    except Exception as e:
        log_lines.append(f"❌ Error opening {file_path}: {e}")
        return

    if isinstance(data, dict) and "messages" in data:
        data["messages"] = [clean_message(msg) for msg in data["messages"]]

        output_path = os.path.join(FOLDER_PATH, "cleaned_" + os.path.basename(file_path))
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            log_lines.append(f"✅ Cleaned: {file_path}")
        except Exception as e:
            log_lines.append(f"❌ Error saving cleaned file {file_path}: {e}")
    else:
        log_lines.append(f"⚠️ Skipped: {file_path} (no 'messages' key or not a dict)")

def process_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            process_file(file_path)

    # Write log to file at the end
    log_path = os.path.join(folder_path, "processing_log.txt")
    with open(log_path, "w", encoding="utf-8") as log_file:
        log_file.write("\n".join(log_lines))
    print(f"\n📄 Log written to {log_path}")

# Run it
process_folder(FOLDER_PATH)
