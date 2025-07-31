import os
import json
import pandas as pd

# Bokeh for plotting
from collections import Counter
from bokeh.layouts import row, column
from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, CheckboxGroup, HoverTool


DATA_PATH = os.getcwd() + "\\Data\\data.json"

# Load data from JSON
with open(DATA_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Convert to Pandas DataFrame for easier filtering
# each row is a course's instance with the corresponding student's year and degree
rows = []
for item in data:
    year = item.get("Year")
    degree = item.get("Degree")
    for course in item.get("CourseList", []):
        rows.append({"Year": year, "Degree": degree, "Course": course})
df = pd.DataFrame(rows)

# get and sort years and degrees for the checkboxes
AllYears = sorted(df["Year"].unique())
AllDegrees = sorted(df["Degree"].unique())

# Set up checkbox widget
YearBox = CheckboxGroup(labels=[str(y) for y in AllYears], active=[5])
DegreeBox = CheckboxGroup(labels=["کارشناسی", "ارشد", "دکتری"], active=[0])

# Function to get course counts for selected years and degrees
def GetCourseCount(SelecYears, SelecDegrees):
    if not SelecYears or not SelecDegrees:
        return ["wtf"], ["wtf"], ["wtf"]
    
    SelecYears = [int(AllYears[i]) for i in SelecYears]
    SelecDegrees = [int(AllDegrees[i]) for i in SelecDegrees]

    filtered = df[
        df["Year"].isin(SelecYears) &
        df["Degree"].isin(SelecDegrees)
    ]
    
    CourseCounts = Counter(filtered["Course"])
    
    # Map course to years
    course_years = (
        filtered.groupby("Course")["Year"]
        .apply(lambda yrs: ', '.join(sorted(map(str, yrs.unique()))))
        .to_dict()
    )

    sorted_courses = sorted(CourseCounts.items(), key=lambda x: x[1], reverse=True)
    if not sorted_courses:
        return [], [], []
    courses, counts = zip(*sorted_courses)
    years_list = [course_years[course] for course in courses]
    return list(courses), list(counts), years_list

# Initial data
initial_courses, initial_counts, initial_years = GetCourseCount(
    YearBox.active,
    DegreeBox.active
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
    height=720,
    width=1360,
    title="Course Frequency by Selected Years",
    toolbar_location="above",
    tools=""
)
p.vbar(x='course', top='count', width=0.95, source=source)
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
    SelecYears = YearBox.active
    SelecDegrees = DegreeBox.active
    courses, counts, years_list = GetCourseCount(SelecYears, SelecDegrees)
    source.data = dict(course=courses, count=counts, years=years_list)
    p.x_range.factors = courses

    SelecYears_labels = [str(AllYears[i]) for i in SelecYears]
    SelecDegrees_labels = [str(AllDegrees[i]) for i in SelecDegrees]
    p.title.text = f"Course Frequency for Years: {', '.join(SelecYears_labels)} | Degrees: {', '.join(SelecDegrees_labels)}"


YearBox.on_change('active', update)
DegreeBox.on_change('active', update)

# Layout: YearBox on left, plot on right
controls = column(YearBox, DegreeBox, width=70)
layout = row(controls, p)
curdoc().add_root(layout)
