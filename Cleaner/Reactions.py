import json
import os

# ✅ CONFIG
INPUT_FILE = r"Your\Path\Here\deduplicated_merged_filtered_messages.json"
OUTPUT_FILE = r"Your\Path\Here\deduplicated_merged_filtered_messages.json"

# ✅ Load JSON
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

messages = data.get("messages", [])

# ✅ Rewrite only .svg paths and warn on others
for msg in messages:
    for reaction in msg.get("reactions", []):
        emoji = reaction.get("emoji", {})
        image_url = emoji.get("imageUrl")

        if isinstance(image_url, str) and "\\" in image_url:
            filename = os.path.basename(image_url)

            if filename.lower().endswith(".svg"):
                emoji["imageUrl"] = f"svg\\{filename}"
            else:
                print(f"⚠️  Non-SVG file detected: {filename} in message ID {msg.get('id')}")

# ✅ Save output
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump({"messages": messages}, f, indent=2, ensure_ascii=False)

print(f"✅ Done. SVG emoji paths rewritten. Output saved to:\n{OUTPUT_FILE}")
input("Press Enter to exit...")