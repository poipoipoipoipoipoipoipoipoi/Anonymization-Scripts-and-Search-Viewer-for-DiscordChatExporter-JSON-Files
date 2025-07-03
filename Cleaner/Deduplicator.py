import json
import os

# ✅ CONFIG
INPUT_FILE = r"Your\Path\Here\merged_filtered_messages.json"
OUTPUT_FILE = r"Your\Path\Here\deduplicated_merged_filtered_messages.json"

# ✅ Load messages
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

messages = data.get("messages", [])

# ✅ Remove 'id' and collect unique messages
seen = set()
deduped_messages = []

for msg in messages:
    msg.pop("id", None)  # Remove ID

    # Serialize message to string for hash comparison
    msg_str = json.dumps(msg, sort_keys=True)

    if msg_str not in seen:
        seen.add(msg_str)
        deduped_messages.append(msg)

# ✅ Save output
output = {"messages": deduped_messages}

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"✅ Done. {len(deduped_messages)} unique messages saved to:\n{OUTPUT_FILE}")
