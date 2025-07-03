import json
import os

# ✅ CONFIG
INPUT_FILE = r"Your\Path\Here\deduplicated_merged_filtered_messages_r.json"
OUTPUT_FILE = r"Your\Path\Here\deduplicated_merged_filtered_messages_r_i.json"

# ✅ Load JSON
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

messages = data.get("messages", [])

# ✅ Function to clean emoji image URLs
def fix_emoji_image_url(url, msg_id, context):
    if not isinstance(url, str) or "\\" not in url:
        return url

    filename = os.path.basename(url)
    if filename.lower().endswith(".svg"):
        return f"svg\\{filename}"
    else:
        print(f"⚠️ Non-SVG file detected in {context}: {filename} (msg ID: {msg_id})")
        return url  # leave unchanged, just warn

# ✅ Process all messages
for msg in messages:
    msg_id = msg.get("id")

    # Fix reactions[*].emoji.imageUrl
    # for reaction in msg.get("reactions", []):
    #     emoji = reaction.get("emoji", {})
    #     if "imageUrl" in emoji:
    #         emoji["imageUrl"] = fix_emoji_image_url(emoji["imageUrl"], msg_id, "reaction")

    # Fix inlineEmojis[*].imageUrl
    for inline in msg.get("inlineEmojis", []):
        if "imageUrl" in inline:
            inline["imageUrl"] = fix_emoji_image_url(inline["imageUrl"], msg_id, "inlineEmoji")

# ✅ Save output
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump({"messages": messages}, f, indent=2, ensure_ascii=False)

print(f"✅ Done. SVG emoji paths rewritten (with warnings for non-SVGs).\nOutput saved to:\n{OUTPUT_FILE}")
input("Press Enter to exit...")
