try:
    import os
    import json
    import re
    from collections import defaultdict
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine
    from presidio_anonymizer.entities import OperatorConfig

    # ---------------------- CONFIG ---------------------- #
    INPUT_FILE = r"Your\Path\Here\deduplicated_merged_filtered_messages_r_i.json"
    OUTPUT_FILE = r"Your\Path\Here\redacted_deduplicated_merged_filtered_messages_r_i.json"
    SCORE_THRESHOLD = 0.7

    NAME_WHITELIST = {n.lower() for n in [
        "Your Text Here", "Your Text Here"
    ]}

    URL_WHITELIST = [
        "Your Text Here", "Your Text Here"
    ]

    # ---------------------- INIT PRESIDIO ---------------------- #
    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()

    # Redaction behavior
    operator_config = {
        "DEFAULT": OperatorConfig("replace", {"new_value": "[REDACTED]"}),
        "PERSON": OperatorConfig("replace", {"new_value": "[REDACTED_NAME]"}),
        "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[REDACTED]"}),
        "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[REDACTED]"}),
        "URL": OperatorConfig("replace", {"new_value": "[REDACTED_URL]"})
    }

    # ---------------------- HELPERS ---------------------- #
    def is_whitelisted_url(url):
        return any(url.startswith(prefix) for prefix in URL_WHITELIST)

    def redact_mentions(text):
        def replace(match):
            username = match.group(1)
            if username.lower() in NAME_WHITELIST:
                return match.group(0)
            return "@[REDACTED_NAME]"
        return re.sub(r"@([^\s\/]{1,64})", replace, text)

    # ---------------------- LOAD DATA ---------------------- #
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    messages = data.get("messages", [])
    pii_counts = defaultdict(int)
    low_score_hits = []

    # ---------------------- PROCESS MESSAGES ---------------------- #
    for msg in messages:
        content = msg.get("content", "")

        # Step 1: Redact mentions
        content = redact_mentions(content)

        # Step 2: Regex URL redaction (unless whitelisted)
        content = re.sub(
            r"https?://[^\s)>\]}]+",
            lambda m: m.group(0) if is_whitelisted_url(m.group(0)) else "[REDACTED_URL]",
            content
        )

        # Step 3: Analyze PII
        results = analyzer.analyze(text=content, language="en")
        filtered_results = []

        for r in results:
            entity_text = content[r.start:r.end]

            # Skip whitelisted names or URLs
            if r.entity_type == "PERSON" and entity_text.lower() in NAME_WHITELIST:
                continue
            if r.entity_type == "URL" and is_whitelisted_url(entity_text):
                continue

            if r.score >= SCORE_THRESHOLD:
                pii_counts[r.entity_type] += 1
                filtered_results.append(r)
            else:
                low_score_hits.append({
                    "text": entity_text,
                    "entity_type": r.entity_type,
                    "score": round(r.score, 3)
                })

        # Step 4: Anonymize
        content = anonymizer.anonymize(
            text=content,
            analyzer_results=filtered_results,
            operators=operator_config
        ).text

        msg["content"] = content

    # ---------------------- SAVE ---------------------- #
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump({"messages": messages}, f, ensure_ascii=False, indent=2)

    # ---------------------- SUMMARY ---------------------- #
    print(f"\n✅ Redacted file saved to:\n{OUTPUT_FILE}")
    print("\n📊 Redacted entity counts:")
    for entity_type, count in pii_counts.items():
        print(f"  {entity_type}: {count}")

    if low_score_hits:
        print("\n⚠️ Low-confidence PII (not redacted, score < {:.2f}):".format(SCORE_THRESHOLD))
        for i, hit in enumerate(low_score_hits[:1000]):
            print(f"  [{hit['score']}] {hit['entity_type']}: \"{hit['text']}\"")
        if len(low_score_hits) > 1000:
            print(f"  ...and {len(low_score_hits) - 1000} more.")
    else:
        print("\n✅ No low-confidence PII found.")

    print("\n✅ Done successfully.")

except Exception as e:
    print(f"\n❌ ERROR OCCURRED: {e}")

# ---------------------- EXIT PAUSE ---------------------- #
input("\nPress Enter to exit...")
