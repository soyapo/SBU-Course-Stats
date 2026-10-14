# SBU Course Stats

A small toolkit for scraping, storing, and visualizing publicly available course-enrollment data of Shahid Beheshti University (SBU) students.

The project crawls SBU's public course-list endpoint, aggregates each student's enrolled courses into JSON, and renders an interactive dashboard that shows how frequently each course is taken — filterable by entry year and degree level.

> **Note:** This project is intended for educational and analytical purposes only, and it operates strictly on data that SBU already exposes publicly. Please use it responsibly.

[فارسی (Persian README)](README.fa.md)

## Features

- **Web crawler** that iterates over student IDs, degrees, entry years, and faculty codes to collect course data.
- **JSON data store** with helpers to add/update students, compute the semester count, and correct degree fields.
- **Interactive dashboards** for exploring course frequency:
  - A static, self-contained HTML dashboard powered by Chart.js.
  - A live Bokeh server dashboard with year/degree checkboxes and hover tooltips.

## Project Structure

| Path | Description |
| --- | --- |
| [Spider.py](Spider.py) | The crawler. Builds SBU IDs from year/degree/faculty/student-id ranges and scrapes each student's course list. |
| [JSONModifier.py](JSONModifier.py) | Reads/writes the JSON data store; adds or updates students, computes semesters, and fixes degree values. |
| [Classes/DataRequest.py](Classes/DataRequest.py) | Wraps the POST request to SBU's `course.list.php` endpoint. |
| [Classes/Student.py](Classes/Student.py) | The `Student` data model (ID, year, degree, faculty, major, course list). |
| [Plot.py](Plot.py) | Interactive Bokeh dashboard for course frequency by selected years/degrees. |
| [site.py](site.py) | Generates a static, self-contained HTML dashboard (`index.html`) from the JSON data. |
| [data/](data/) | Scraped course data, one JSON file per faculty/degree group. |
| [index.html](index.html) | The generated static dashboard. |

## How an SBU ID Is Built

Each student ID is composed as:

```
<entry year (2 digits)> + <degree (1 digit)> + <faculty (2 digits)> + <student number (3 digits)>
```

- **Degree:** `2` bachelor, `4` master's, `5` PhD.
- **Faculty:** e.g. `22` for Mathematics.

The crawler posts this ID to the endpoint and parses the returned HTML for the student's course list.

## Requirements

- Python 3.9+
- Dependencies:

```bash
pip install requests beautifulsoup4 pandas bokeh
```

## Usage

### 1. Scrape data

Configure the `faculty`, degree range, and entry-year range in [Spider.py](Spider.py), then run:

```bash
python Spider.py
```

Scraped students are written to the JSON file configured in [JSONModifier.py](JSONModifier.py) (`DATA_PATH`).

### 2. Generate the static dashboard

```bash
python site.py
```

This produces `index.html`, which you can open directly in any browser — no server required.

### 3. (Optional) Run the live Bokeh dashboard

```bash
bokeh serve --show Plot.py
```

## Configuration Notes

- Set `DATA_PATH` in [JSONModifier.py](JSONModifier.py) and [Plot.py](Plot.py) / [site.py](site.py) to point at the JSON file you want to work with.
- Adjust the `year`, `deg`, and `faculty` loops in [Spider.py](Spider.py) to target the cohort you care about.

## Acknowledgements

During development, **ChatGPT** and **Claude** were used as coding assistants — for drafting and refactoring parts of the code, generating the dashboard's front-end, and writing documentation. All generated output was reviewed before being committed.

## Disclaimer

This tool only accesses data that Shahid Beheshti University already makes publicly available through its own endpoints. It is provided for educational and research purposes. Use it in accordance with SBU's terms of service and applicable laws.
