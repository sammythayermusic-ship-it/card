#!/usr/bin/env python3
"""
Rebuilds the contact files behind each card's "Add to Contacts" button.

Change a person's info in the CARDS block below, then run this from the
site folder:

    python3 tools/make_vcard.py

It rewrites every card's .vcf file with that person's photo baked in.
Needs nothing installed beyond Python 3.
"""
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------- One block per card ----------
CARDS = [
    {
        "first": "Sammy",
        "last": "Thayer",
        "company": "Mowa Smart Properties",
        "title": "Founder",
        "phone": "+12072284511",
        "email": "sammy@mowaproperties.com",
        "links": [
            ("Website", "https://mowaproperties.com"),
            ("LinkedIn", "https://www.linkedin.com/in/sammythayer"),
            ("X", "https://x.com/sammy_sound207"),
        ],
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
    },
    {
        "first": "Frank",
        "last": "Curran",
        "company": "Harborview Properties",
        "title": "Real Estate Agent",
        "phone": "+12077762813",
        "email": "fcurran@harborviewproperties.com",
        "links": [
            ("Website", "https://harborviewproperties.com"),
            ("LinkedIn", "https://www.linkedin.com/in/frank-curran-2627a3202/"),
        ],
        "city": "Portland",
        "state": "ME",
        "note": (
            "Real Estate Agent at Harborview Properties. Residential and "
            "commercial real estate in Greater Portland, Maine."
        ),
        "photo": "frank-curran/assets/frank.jpg",
        "output": "frank-curran/frank-curran.vcf",
    },
]
# ----------------------------------------


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


def build(i):
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
    ]
    for n, (label, url) in enumerate(i["links"], start=1):
        lines += [f"item{n}.URL:{url}", f"item{n}.X-ABLabel:{label}"]
    lines += [
        f"ADR;TYPE=WORK:;;;{esc(i['city'])};{esc(i['state'])};;USA",
        f"NOTE:{esc(i['note'])}",
        f"PHOTO;ENCODING=b;TYPE=JPEG:{photo}",
        "END:VCARD",
    ]
    out = ROOT / i["output"]
    out.write_bytes(("\r\n".join(fold(l) for l in lines) + "\r\n").encode("utf-8"))
    print(f"Wrote {i['output']} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    for card in CARDS:
        build(card)
