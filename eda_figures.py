"""
Generate exploratory-data-analysis figures for the technical report.

Figures are chosen to motivate the machine-learning tasks (sparsity, basket
size, cohort structure, preprocessing impact). Labels are kept ASCII/English so
the plots render reliably without a Persian font; course *names* are referenced
in the report text/tables instead of on the axes.

Output: assets/figures/*.png
"""

import os
import json
from collections import Counter

import numpy as np
import matplotlib.pyplot as plt

from preprocessing import SNAPSHOTS, OUT_DIR, DATA_DIR, run as run_preprocessing

FIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "figures")
SEM_LABELS = {"22-4032": "1403-S2", "22-4041": "1404-S1", "22-4042": "1404-S2",
              "22-4051": "1405-S1"}
DEG_LABELS = {2: "Bachelor", 4: "Master", 5: "PhD"}
# Fixed-order categorical palette, one slot per semester (validated for
# color-vision deficiency); add a slot when a snapshot is added.
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
GROUP_WIDTH = 0.8  # total width of one group of per-semester bars

plt.rcParams.update({"figure.dpi": 130, "font.size": 11, "axes.grid": True,
                     "grid.alpha": 0.3, "axes.axisbelow": True})


def load_raw(code):
    with open(os.path.join(DATA_DIR, code + ".json"), "r", encoding="utf-8") as f:
        return json.load(f)


def load_canon(code):
    with open(os.path.join(OUT_DIR, code + ".canonical.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def bar_offset(i):
    """Center offset of semester i's bar within a group of len(SNAPSHOTS) bars."""
    return (i - (len(SNAPSHOTS) - 1) / 2) * GROUP_WIDTH / len(SNAPSHOTS)


def fig_degree_distribution():
    degs = [2, 4, 5]
    fig, ax = plt.subplots(figsize=(7, 4.2))
    x = np.arange(len(degs))
    w = GROUP_WIDTH / len(SNAPSHOTS)
    for i, code in enumerate(SNAPSHOTS):
        counts = Counter(s["Degree"] for s in load_raw(code))
        ax.bar(x + bar_offset(i), [counts.get(d, 0) for d in degs], w,
               label=SEM_LABELS[code], color=COLORS[i])
    ax.set_xticks(x, [DEG_LABELS[d] for d in degs])
    ax.set_ylabel("Number of students")
    ax.set_title("Student population by degree, per semester")
    ax.legend(title="Semester")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "degree_distribution.png"))
    plt.close(fig)


def fig_year_distribution():
    years = sorted({s["Year"] for code in SNAPSHOTS for s in load_raw(code)})
    fig, ax = plt.subplots(figsize=(8, 4.2))
    x = np.arange(len(years))
    w = GROUP_WIDTH / len(SNAPSHOTS)
    for i, code in enumerate(SNAPSHOTS):
        counts = Counter(s["Year"] for s in load_raw(code))
        ax.bar(x + bar_offset(i), [counts.get(y, 0) for y in years], w,
               label=SEM_LABELS[code], color=COLORS[i])
    ax.set_xticks(x, [str(y) for y in years])
    ax.set_xlabel("Entry year")
    ax.set_ylabel("Number of students")
    ax.set_title("Cohort size by entry year, per semester")
    ax.legend(title="Semester")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "year_distribution.png"))
    plt.close(fig)


def fig_courses_per_student():
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    bins = np.arange(0, 16) - 0.5
    for i, code in enumerate(SNAPSHOTS):
        sizes = [len(s["CourseIDs"]) for s in load_canon(code)]
        ax.hist(sizes, bins=bins, histtype="step", linewidth=2,
                label=f"{SEM_LABELS[code]} (median {int(np.median(sizes))})",
                color=COLORS[i])
    ax.set_xlabel("Courses per student (basket size)")
    ax.set_ylabel("Number of students")
    ax.set_title("Distribution of basket size (courses taken per semester)")
    ax.set_xlim(0, 15)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "courses_per_student.png"))
    plt.close(fig)


def fig_course_popularity_longtail():
    """Frequency-vs-rank on log-log: shows the long-tail sparsity ML must handle."""
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    for i, code in enumerate(SNAPSHOTS):
        freq = Counter(cid for s in load_canon(code) for cid in s["CourseIDs"])
        ranked = sorted(freq.values(), reverse=True)
        ax.loglog(range(1, len(ranked) + 1), ranked, marker=".", linestyle="-",
                  markersize=4, label=SEM_LABELS[code], color=COLORS[i])
    ax.set_xlabel("Course rank (most to least enrolled)")
    ax.set_ylabel("Enrollment count")
    ax.set_title("Course popularity is long-tailed (log-log)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "course_popularity_longtail.png"))
    plt.close(fig)


def fig_canonicalization_impact():
    """Vocabulary before/after canonicalization and shared-across-semesters count."""
    raw_sets, canon_sets = [], []
    for code in SNAPSHOTS:
        raw_sets.append(set(c for s in load_raw(code) for c in s["CourseList"]))
        canon_sets.append(set(cid for s in load_canon(code) for cid in s["CourseIDs"]))
    raw_union = len(set().union(*raw_sets))
    canon_union = len(set().union(*canon_sets))
    raw_shared = len(set.intersection(*raw_sets))
    canon_shared = len(set.intersection(*canon_sets))

    fig, ax = plt.subplots(figsize=(7, 4.2))
    groups = ["Total vocabulary\n(union)", f"Shared by all {len(SNAPSHOTS)}\nsemesters"]
    x = np.arange(len(groups))
    w = 0.35
    ax.bar(x - w / 2, [raw_union, raw_shared], w, label="Raw", color=COLORS[0])
    ax.bar(x + w / 2, [canon_union, canon_shared], w, label="Canonicalized", color=COLORS[1])
    for xi, (rv, cv) in zip(x, [(raw_union, canon_union), (raw_shared, canon_shared)]):
        ax.text(xi - w / 2, rv + 4, str(rv), ha="center", fontsize=9)
        ax.text(xi + w / 2, cv + 4, str(cv), ha="center", fontsize=9)
    ax.set_xticks(x, groups)
    ax.set_ylabel("Distinct courses")
    ax.set_title("Effect of Phase 0 canonicalization on the course vocabulary")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "canonicalization_impact.png"))
    plt.close(fig)


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    if not all(os.path.exists(os.path.join(OUT_DIR, code + ".canonical.json"))
               for code in SNAPSHOTS):
        run_preprocessing()
    fig_degree_distribution()
    fig_year_distribution()
    fig_courses_per_student()
    fig_course_popularity_longtail()
    fig_canonicalization_impact()
    print("Figures written to", FIG_DIR)


if __name__ == "__main__":
    main()
