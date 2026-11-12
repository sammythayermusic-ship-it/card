#!/usr/bin/env python3
"""
Rebuilds sammy-thayer.vcf (the file behind the "Add to Contacts" button).

Change your info in the INFO block below, then run:

    python3 tools/make_vcard.py

It rewrites sammy-thayer.vcf in the main folder, with the photo from
assets/sammy.jpg baked in. Needs nothing installed beyond Python 3.
"""
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------- Your info ----------
INFO = {
    "first": "Sammy",
    "last": "Thayer",
    "company": "Mowa Smart Properties",
    "title": "Founder",
    "phone": "+12072284511",
    "email": "sammy@mowaproperties.com",
    "website": "https://mowaproperties.com",
    "linkedin": "https://www.linkedin.com/in/sammythayer",
    "x": "https://x.com/sammy_sound207",
    "city": "Portland",
    "state": "ME",
    "note": (
        "Founder, Mowa Smart Properties: AI integration and automation for "
        "businesses, robotic lawn care, smart property care, and property "
        "management. Group Creative Director of AI & Operations for Shipyard "
        "Brewing Co. and Harborview Properties. Audio engineer (FOH, "
        "production, tour management for 12/OC). X: @sammy_sound207"
    ),
    "photo": "assets/sammy.jpg",
    "output": "sammy-thayer.vcf",
}
# -------------------------------


def esc(text):
    """Escape the characters vCard treats as special."""
    return (
        text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")
    )


def fold(line):
    """vCard lines are capped at 75 bytes; longer ones continue on the next line after a space."""
    raw = line.encode("utf-8")
    if len(raw) <= 75:
        return line
    parts, first = [], True
    while raw:
        size = 75 if first else 74
        chunk = raw[:size]
        # don't cut a multi-byte character in half
        while len(chunk) < len(raw) and (raw[len(chunk)] & 0xC0) == 0x80:
            chunk = chunk[:-1]
        parts.append(chunk.decode("utf-8"))
        raw = raw[len(chunk):]
        first = False
    return "\r\n ".join(parts)


def build():
    i = INFO
    photo = base64.b64encode((ROOT / i["photo"]).read_bytes()).decode("ascii")
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{esc(i['last'])};{esc(i['first'])};;;",
        f"FN:{esc(i['first'])} {esc(i['last'])}",
        f"ORG:{esc(i['company'])}",
        f"TITLE:{esc(i['title'])}",
        f"TEL;TYPE=CELL,VOICE:{i['phone']}",
        f"EMAIL;TYPE=INTERNET,WORK:{i['email']}",
        f"item1.URL:{i['website']}",
        "item1.X-ABLabel:Website",
        f"item2.URL:{i['linkedin']}",
        "item2.X-ABLabel:LinkedIn",
        f"item3.URL:{i['x']}",
        "item3.X-ABLabel:X",
        f"ADR;TYPE=WORK:;;;{esc(i['city'])};{esc(i['state'])};;USA",
        f"NOTE:{esc(i['note'])}",
        f"PHOTO;ENCODING=b;TYPE=JPEG:{photo}",
        "END:VCARD",
    ]
    out = ROOT / i["output"]
    out.write_bytes(("\r\n".join(fold(l) for l in lines) + "\r\n").encode("utf-8"))
    print(f"Wrote {out.name} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    build()
