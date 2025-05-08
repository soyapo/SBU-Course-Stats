import json
from collections import Counter
from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource
from bokeh.layouts import column

# Load JSON data
with open('data.json', 'r', encoding='utf-8') as f:
    records = json.load(f)

# Flatten all CourseLists
all_courses = []
for item in records:
    all_courses.extend(item.get('CourseList', []))

# Count frequencies
course_counts = Counter(all_courses)
sorted_courses = sorted(course_counts.items(), key=lambda x: x[1], reverse=True)
course_names, frequencies = zip(*sorted_courses)

# Create Bokeh plot
source = ColumnDataSource(data=dict(course=course_names, count=frequencies))

p = figure(x_range=course_names, height=400, title="Course Frequency",
           toolbar_location=None, tools="", sizing_mode='stretch_width')

p.vbar(x='course', top='count', width=0.8, source=source)
p.xaxis.major_label_orientation = 1.2
p.xaxis.axis_label = "Course Name"
p.yaxis.axis_label = "Frequency"

curdoc().add_root(column(p))
