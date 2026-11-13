"""Extract one mahberet from the Ben-Yehuda dump and split it into lines.

Usage: py -3.13 scripts/extract_hebrew.py <dump.txt> <number 1-28> <out.json>

Output: JSON list of blocks; each block is a list of Hebrew lines.
A block is a paragraph of the source. A line is one rhyme unit
(the source marks these with " / ") or one line of verse.
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

NIQQUD = re.compile(r"[֑-ׇ]")
HEADING = re.compile(r"^המחברת ה")
# Speaker formulas of the dialogue; a new line starts before each one.
SPEAKERS = ["ואען ואמר:", "ויאמר השר:"]


def strip(s: str) -> str:
    return NIQQUD.sub("", s)


def main() -> None:
    dump, number, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    lines = open(dump, encoding="utf-8").read().split("\n")
    heads = [i for i, l in enumerate(lines) if HEADING.match(strip(l).strip())]
    if len(heads) != 28:
        sys.exit(f"expected 28 headings, found {len(heads)}")
    start = heads[number - 1]
    end = heads[number] if number < 28 else len(lines)
    title = lines[start].strip()
    body = "\n".join(lines[start + 1:end])

    blocks = []
    for para in re.split(r"\n\s*\n", body):
        para = " ".join(para.split())
        if not para:
            continue
        if any(strip(para).startswith(sp) for sp in SPEAKERS):
            # a dialogue turn that the source prints inside a paragraph
            for sp in SPEAKERS:
                pat = "".join(re.escape(c) + "[֑-ׇ]*" if c.isalpha() else re.escape(c) for c in sp)
                para = re.sub(r"(?<=\S) (" + pat + ")", r"\n\1", para)
        for turn in para.split("\n"):
            segs = [s.strip() for s in turn.split("/") if s.strip()]
            if segs:
                blocks.append(segs)

    json.dump({"title": title, "blocks": blocks}, open(out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    n = sum(len(b) for b in blocks)
    print(f"{strip(title)}: {len(blocks)} blocks, {n} lines -> {out}")
    for i, b in enumerate(blocks):
        print(i, len(b), " | ".join(" ".join(strip(s).split()[:2]) for s in b))


if __name__ == "__main__":
    main()
