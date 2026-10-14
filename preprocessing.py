"""
Phase 0 - Course-name canonicalization for the SBU Course Stats dataset.

The raw scraped course names suffer from orthographic fragmentation: the same
course appears under many string variants (Arabic vs. Persian letters, ZWNJ vs.
space, section prefixes, stray course-code suffixes). This module produces a
single canonical form per course and a frozen canonical-name -> integer id map
that is SHARED across all semester snapshots.

Design decisions (fixed by project owner):
  * Recitation classes ("کلاس حل تمرین X") are MERGED into their parent course X.
  * Laboratory units ("آزمایشگاه X") are kept SEPARATE (distinct courses).
  * Numbered courses ("ریاضی عمومی 1" vs "... 2") are kept DISTINCT
    -> trailing standalone numbers are preserved.
  * Spellings that differ only by LOOKALIKE characters are MERGED
    ("جزئی"/"جزیی", "فرآیند"/"فرایند", "جبرخطی"/"جبر خطی"); the most frequent
    spelling becomes the canonical name.
  * Different names are never merged, even when related
    ("یادگیری آماری" vs "یادگیری آماری مقدماتی", "اصول حسابداری" vs "... 1").

The snapshots are never merged; each is canonicalized independently and
written to its own output file. Only the vocabulary (course-id map) is shared.
"""

import os
import re
import json
import unicodedata

# --- paths -------------------------------------------------------------------
ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, "data")
OUT_DIR = os.path.join(DATA_DIR, "canonical")

# Chronological order of the semester snapshots (do NOT merge these).
SNAPSHOTS = ["22-4032", "22-4041", "22-4042", "22-4051"]

# --- character-level normalization -------------------------------------------
# Arabic -> Persian letter unification and other Persian text fixes.
_CHAR_MAP = {
    "ي": "ی",  # ARABIC YEH   -> PERSIAN YEH
    "ى": "ی",  # ALEF MAKSURA -> PERSIAN YEH
    "ك": "ک",  # ARABIC KAF   -> KEHEH (Persian kaf)
    "ة": "ه",  # TEH MARBUTA  -> HEH
    "‌": " ",       # ZERO WIDTH NON-JOINER -> space
    "​": "",        # ZERO WIDTH SPACE       -> remove
    "‏": "",        # RTL MARK               -> remove
    "‎": "",        # LTR MARK               -> remove
    "ـ": "",        # TATWEEL (kashida)      -> remove
}
_CHAR_TABLE = {ord(k): v for k, v in _CHAR_MAP.items()}

# Arabic-Indic (U+0660-0669) and Persian (U+06F0-06F9) digits -> ASCII.
for _base in (0x0660, 0x06F0):
    for _d in range(10):
        _CHAR_TABLE[_base + _d] = str(_d)

_GR_PREFIX = re.compile(r"^Gr\d+\s*-\s*")            # e.g. "Gr01-"
_RECITATION = re.compile(r"^کلاس\s+حل\s+تمرین\s+")   # recitation phrase
_TRAILING_CODE = re.compile(r"\s*\([^)]*\)\s*$")     # stray "(4012430103895)"
_WS = re.compile(r"\s+")


def normalize_course(name):
    """Return the canonical form of a raw course name."""
    s = unicodedata.normalize("NFKC", name)
    s = s.translate(_CHAR_TABLE)
    s = _TRAILING_CODE.sub("", s)      # drop trailing "(code)" suffixes
    s = _GR_PREFIX.sub("", s)          # drop "Gr0N-" section marker
    s = _RECITATION.sub("", s)         # merge recitation -> parent course
    s = _WS.sub(" ", s).strip()        # collapse whitespace
    return s


# --- lookalike folding -------------------------------------------------------
# Letters that differ only by a hamza/madda mark from their base letter.
_LOOKALIKE_TABLE = str.maketrans({
    "ئ": "ی",  # YEH WITH HAMZA ABOVE  -> YEH   (جزئی / جزیی)
    "آ": "ا",  # ALEF WITH MADDA ABOVE -> ALEF  (فرآیند / فرایند)
    "أ": "ا",  # ALEF WITH HAMZA ABOVE -> ALEF
    "إ": "ا",  # ALEF WITH HAMZA BELOW -> ALEF
    "ؤ": "و",  # WAW WITH HAMZA ABOVE  -> WAW
    "ۀ": "ه",  # HEH WITH YEH ABOVE    -> HEH
})
# A space that changes no letter shape: after a letter that never joins
# leftward (ا د ذ ر ز ژ و) or a digit, or before a digit. "جبرخطی" and
# "جبر خطی" render almost identically; a space after a joining letter does not.
_SHAPE_NEUTRAL_SPACE = re.compile(r"(?<=[ادذرزژو\d])\s+|\s+(?=\d)")


def lookalike_key(name):
    """Fold a normalized name so spellings that look alike collide.

    Used only to group names; the folded key is never shown or stored.
    """
    return _SHAPE_NEUTRAL_SPACE.sub("", name.translate(_LOOKALIKE_TABLE))


# --- snapshot IO -------------------------------------------------------------
def load_snapshot(code):
    with open(os.path.join(DATA_DIR, code + ".json"), "r", encoding="utf-8") as f:
        return json.load(f)


def build_vocabulary(snapshots=SNAPSHOTS):
    """Build a frozen canonical-name -> id map shared across all snapshots.

    Normalized names with the same lookalike_key are one course; the most
    frequent spelling (then alphabetical) is its canonical name. Also returns
    `spelling`, mapping every normalized name to that canonical name.

    IDs are assigned by descending frequency (id 0 = most common course), then
    alphabetically to break ties, so the mapping is deterministic.
    """
    name_freq = {}
    for code in snapshots:
        for student in load_snapshot(code):
            for raw in student["CourseList"]:
                name = normalize_course(raw)
                name_freq[name] = name_freq.get(name, 0) + 1

    groups = {}
    for name in name_freq:
        groups.setdefault(lookalike_key(name), []).append(name)
    spelling, freq = {}, {}
    for names in groups.values():
        canon = min(names, key=lambda n: (-name_freq[n], n))
        freq[canon] = sum(name_freq[n] for n in names)
        for name in names:
            spelling[name] = canon

    ordered = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))
    vocab = {name: i for i, (name, _) in enumerate(ordered)}
    return vocab, freq, spelling


def canonicalize_snapshot(code, vocab, spelling):
    """Return a snapshot with canonicalized CourseList (raw file untouched).

    Adds a parallel "CourseIDs" field and de-duplicates courses within a
    student (recitation merged into its parent can create a duplicate).
    """
    out = []
    for student in load_snapshot(code):
        seen, courses, ids = set(), [], []
        for raw in student["CourseList"]:
            canon = spelling[normalize_course(raw)]
            if canon in seen:
                continue
            seen.add(canon)
            courses.append(canon)
            ids.append(vocab[canon])
        s = dict(student)
        s["CourseList"] = courses
        s["CourseIDs"] = ids
        out.append(s)
    return out


def run():
    os.makedirs(OUT_DIR, exist_ok=True)
    vocab, freq, spelling = build_vocabulary()

    # Persist the shared vocabulary.
    with open(os.path.join(OUT_DIR, "course_vocab.json"), "w", encoding="utf-8") as f:
        json.dump(vocab, f, ensure_ascii=False, indent=2)

    # Persist raw -> canonical map (audit trail of every merge performed).
    raw_map = {}
    for code in SNAPSHOTS:
        for student in load_snapshot(code):
            for raw in student["CourseList"]:
                raw_map[raw] = spelling[normalize_course(raw)]
    with open(os.path.join(OUT_DIR, "raw_to_canonical.json"), "w", encoding="utf-8") as f:
        json.dump(raw_map, f, ensure_ascii=False, indent=2)

    # Canonicalize each snapshot independently (files stay separate).
    per_snapshot = {}
    for code in SNAPSHOTS:
        canon = canonicalize_snapshot(code, vocab, spelling)
        with open(os.path.join(OUT_DIR, code + ".canonical.json"), "w", encoding="utf-8") as f:
            json.dump(canon, f, ensure_ascii=False, indent=4)
        per_snapshot[code] = canon

    return vocab, freq, raw_map, per_snapshot


if __name__ == "__main__":
    vocab, freq, raw_map, per_snapshot = run()
    raw_variants = len(raw_map)
    canon_terms = len(vocab)
    merged = raw_variants - canon_terms
    print(f"Raw distinct strings : {raw_variants}")
    print(f"Canonical courses    : {canon_terms}")
    print(f"Variants merged away : {merged}  ({merged / raw_variants:.0%})")
    for code, students in per_snapshot.items():
        vocab_here = {cid for s in students for cid in s["CourseIDs"]}
        print(f"  {code}: {len(students)} students, {len(vocab_here)} distinct courses")
