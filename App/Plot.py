import os
import json
import pandas as pd

from collections import Counter
from bokeh.layouts import row, column
from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, CheckboxGroup, HoverTool


DATA_PATH = os.getcwd() + "\\App\\Data\\data.json"

# Load data from JSON
with open(DATA_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Convert to DataFrame for easier filtering
rows = []
for item in data:
    year = item.get("Year")
    degree = item.get("Degree")
    for course in item.get("CourseList", []):
        rows.append({"Year": year, "Degree": degree, "Course": course})
df = pd.DataFrame(rows)

# Get all unique years for the checkboxes
all_years = sorted(df["Year"].unique())
all_degrees = sorted(df["Degree"].dropna().unique().astype(int))


# Set up checkbox widget
year_checkbox = CheckboxGroup(labels=[str(y) for y in all_years], active=[5])  # Select first year by default
degree_checkbox = CheckboxGroup(labels=[str(d) for d in all_degrees], active=[0])

# Function to get course counts for selected years
def get_course_counts(selected_years, selected_degrees):
    if not selected_years or not selected_degrees:
        return [], [], []
    
    selected_years = [int(all_years[i]) for i in selected_years]
    selected_degrees = [int(all_degrees[i]) for i in selected_degrees]

    filtered = df[
        df["Year"].isin(selected_years) &
        df["Degree"].isin(selected_degrees)
    ]
    
    course_counts = Counter(filtered["Course"])
    
    # Map course to years (optional tooltip detail)
    course_years = (
        filtered.groupby("Course")["Year"]
        .apply(lambda yrs: ', '.join(sorted(map(str, yrs.unique()))))
        .to_dict()
    )

    sorted_courses = sorted(course_counts.items(), key=lambda x: x[1], reverse=True)
    if not sorted_courses:
        return [], [], []
    courses, counts = zip(*sorted_courses)
    years_list = [course_years[course] for course in courses]
    return list(courses), list(counts), years_list

# Initial data
initial_courses, initial_counts, initial_years = get_course_counts(
    year_checkbox.active,
    degree_checkbox.active
)
source = ColumnDataSource(
    data=dict(
        course=initial_courses, 
        count=initial_counts, 
        years=initial_years)
)

# Plot setup
p = figure(
    x_range=initial_courses,
    height=800,
    width=1600,
    title="Course Frequency by Selected Years",
    toolbar_location="above",
    tools=""
)
p.vbar(x='course', top='count', width=0.8, source=source)
p.xaxis.major_label_orientation = 1.5
p.xaxis.major_label_text_font_size = "8pt"
p.xaxis.axis_label = "Course Name"
p.yaxis.axis_label = "Frequency"


# Add hover tool
hover = HoverTool(tooltips=[
    ("Course", "@course"),
    ("Count", "@count"),
    ("Years", "@years")
])
p.add_tools(hover)


# Callback function
def update(attr, old, new):
    selected_years = year_checkbox.active
    selected_degrees = degree_checkbox.active
    courses, counts, years_list = get_course_counts(selected_years, selected_degrees)
    source.data = dict(course=courses, count=counts, years=years_list)
    p.x_range.factors = courses

    selected_years_labels = [str(all_years[i]) for i in selected_years]
    selected_degrees_labels = [str(all_degrees[i]) for i in selected_degrees]
    p.title.text = f"Course Frequency for Years: {', '.join(selected_years_labels)} | Degrees: {', '.join(selected_degrees_labels)}"


year_checkbox.on_change('active', update)
degree_checkbox.on_change('active', update)

# Layout: year_checkbox on left, plot on right
controls = column(year_checkbox, degree_checkbox, width=70)
layout = row(controls, p)
curdoc().add_root(layout)
