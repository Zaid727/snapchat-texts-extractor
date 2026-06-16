import re

INPUT_FILE = "chat_transcript.txt"
OUTPUT_FILE = "cleaned_chat.txt"

# ---------------------------------
# PATTERNS
# ---------------------------------

TIME_PATTERN = re.compile(
    r'(\d{1,2}:\d{2}\s?(?:AM|PM))',
    re.IGNORECASE
)

SENDER_PATTERN = re.compile(
    r'^(ME|MD ZAID SUTAR)\s+(\d{1,2}:\d{2}\s?(?:AM|PM))',
    re.IGNORECASE
)

JUNK_PATTERNS = [

    r'^\d{1,2}:\d{2}\s+.*$',      # status bar

    r'^<.*Md Zaid Sutar.*$',

    r'^©.*$',
    r'^=.*$',
    r'^@.*$',

    r'^CHAT TRANSCRIPT$',
    r'^END OF CHAT$',

    r'^-+$',
    r'^=+$',

    r'^--- Screenshot.*$',

    r'^\s*$'
]

# ---------------------------------
# CLEAN LINE
# ---------------------------------

def is_junk(line):

    line = line.strip()

    for pattern in JUNK_PATTERNS:
        if re.match(pattern, line, re.IGNORECASE):
            return True

    return False

# ---------------------------------
# READ FILE
# ---------------------------------

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    raw_lines = f.readlines()

# ---------------------------------
# REMOVE JUNK
# ---------------------------------

lines = []

for line in raw_lines:

    line = line.strip()

    if is_junk(line):
        continue

    lines.append(line)

# ---------------------------------
# BUILD MESSAGES
# ---------------------------------

messages = []

current_sender = None
current_time = None
current_text = []

for line in lines:

    sender_match = SENDER_PATTERN.match(line)

    if sender_match:

        # save previous message
        if current_sender and current_text:

            messages.append({
                "sender": current_sender,
                "time": current_time,
                "text": " ".join(current_text)
            })

        current_sender = sender_match.group(1)
        current_time = sender_match.group(2)

        remaining = line[sender_match.end():].strip()

        current_text = []

        if remaining:
            current_text.append(remaining)

    else:

        if current_sender:
            current_text.append(line)

# last message

if current_sender and current_text:

    messages.append({
        "sender": current_sender,
        "time": current_time,
        "text": " ".join(current_text)
    })

# ---------------------------------
# REMOVE DUPLICATES
# ---------------------------------

seen = set()
clean_messages = []

for msg in messages:

    key = (
        msg["sender"],
        msg["time"],
        msg["text"]
    )

    if key in seen:
        continue

    seen.add(key)
    clean_messages.append(msg)

# ---------------------------------
# WRITE OUTPUT
# ---------------------------------

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    f.write("=" * 60 + "\n")
    f.write("CLEANED CHAT\n")
    f.write("=" * 60 + "\n\n")

    for msg in clean_messages:

        f.write(
            f"[{msg['sender']}] ({msg['time']})\n"
        )

        f.write(msg["text"] + "\n\n")

        f.write("-" * 60 + "\n\n")

print(
    f"Done! Cleaned transcript saved as: {OUTPUT_FILE}"
)
