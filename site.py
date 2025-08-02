import os
import json
import pandas as pd


def generate_html_dashboard(data_path="data\\data.json", output_path="index.html"):

    # Load data from JSON
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find data file at {data_path}")
        return False
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {data_path}")
        return False

    # Convert to the format needed for processing
    rows = []
    for item in data:
        year = item.get("Year")
        degree = item.get("Degree")
        for course in item.get("CourseList", []):
            rows.append({"Year": year, "Degree": degree, "Course": course})

    df = pd.DataFrame(rows)

    # Get unique years and degrees for the interface
    all_years = sorted(df["Year"].unique())
    all_degrees = sorted(df["Degree"].unique())

    # Convert data to JavaScript format
    js_data = json.dumps(data, ensure_ascii=False, indent=8)

    # Create the HTML content
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Course Frequency Analysis Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <style>
        /* From Uiverse.io by Galahhad */ 
        .theme-switch {{
          font-size: 0.6rem; /* smaller size */
          position: absolute;
          top: 20px;
          right: 30px;
          z-index: 1000;
          --toggle-size: 30px;
          /* the size is adjusted using font-size,
             this is not transform scale,
             so you can choose any size */
          --container-width: 5.625em;
          --container-height: 2.5em;
          --container-radius: 6.25em;
          /* radius 0 - minecraft mode :) */
          --container-light-bg: #3D7EAE;
          --container-night-bg: #1D1F2C;
          --circle-container-diameter: 3.375em;
          --sun-moon-diameter: 2.125em;
          --sun-bg: #ECCA2F;
          --moon-bg: #C4C9D1;
          --spot-color: #959DB1;
          --circle-container-offset: calc((var(--circle-container-diameter) - var(--container-height)) / 2 * -1);
          --stars-color: #fff;
          --clouds-color: #F3FDFF;
          --back-clouds-color: #AACADF;
          --transition: .5s cubic-bezier(0, -0.02, 0.4, 1.25);
          --circle-transition: .3s cubic-bezier(0, -0.02, 0.35, 1.17);
        }}

        .theme-switch, .theme-switch *, .theme-switch *::before, .theme-switch *::after {{
          -webkit-box-sizing: border-box;
          box-sizing: border-box;
          margin: 0;
          padding: 0;
          font-size: 0.7rem;
        }}

        .theme-switch__container {{
          width: var(--container-width);
          height: var(--container-height);
          background-color: var(--container-light-bg);
          border-radius: var(--container-radius);
          overflow: hidden;
          cursor: pointer;
          -webkit-box-shadow: 0em -0.062em 0.062em rgba(0, 0, 0, 0.25), 0em 0.062em 0.125em rgba(255, 255, 255, 0.94);
          box-shadow: 0em -0.062em 0.062em rgba(0, 0, 0, 0.25), 0em 0.062em 0.125em rgba(255, 255, 255, 0.94);
          -webkit-transition: var(--transition);
          -o-transition: var(--transition);
          transition: var(--transition);
          position: relative;
        }}

        .theme-switch__container::before {{
          content: "";
          position: absolute;
          z-index: 1;
          inset: 0;
          -webkit-box-shadow: 0em 0.05em 0.187em rgba(0, 0, 0, 0.25) inset, 0em 0.05em 0.187em rgba(0, 0, 0, 0.25) inset;
          box-shadow: 0em 0.05em 0.187em rgba(0, 0, 0, 0.25) inset, 0em 0.05em 0.187em rgba(0, 0, 0, 0.25) inset;
          border-radius: var(--container-radius)
        }}

        .theme-switch__checkbox {{
          display: none;
        }}

        .theme-switch__circle-container {{
          width: var(--circle-container-diameter);
          height: var(--circle-container-diameter);
          background-color: rgba(255, 255, 255, 0.1);
          position: absolute;
          left: var(--circle-container-offset);
          top: var(--circle-container-offset);
          border-radius: var(--container-radius);
          -webkit-box-shadow: inset 0 0 0 3.375em rgba(255, 255, 255, 0.1), inset 0 0 0 3.375em rgba(255, 255, 255, 0.1), 0 0 0 0.625em rgba(255, 255, 255, 0.1), 0 0 0 1.25em rgba(255, 255, 255, 0.1);
          box-shadow: inset 0 0 0 3.375em rgba(255, 255, 255, 0.1), inset 0 0 0 3.375em rgba(255, 255, 255, 0.1), 0 0 0 0.625em rgba(255, 255, 255, 0.1), 0 0 0 1.25em rgba(255, 255, 255, 0.1);
          display: -webkit-box;
          display: -ms-flexbox;
          display: flex;
          -webkit-transition: var(--circle-transition);
          -o-transition: var(--circle-transition);
          transition: var(--circle-transition);
          pointer-events: none;
        }}

        .theme-switch__sun-moon-container {{
          pointer-events: auto;
          position: relative;
          z-index: 2;
          width: var(--sun-moon-diameter);
          height: var(--sun-moon-diameter);
          margin: auto;
          border-radius: var(--container-radius);
          background-color: var(--sun-bg);
          -webkit-box-shadow: 0.062em 0.062em 0.062em 0em rgba(254, 255, 239, 0.61) inset, 0em -0.062em 0.062em 0em #a1872a inset;
          box-shadow: 0.062em 0.062em 0.062em 0em rgba(254, 255, 239, 0.61) inset, 0em -0.062em 0.062em 0em #a1872a inset;
          -webkit-filter: drop-shadow(0.062em 0.125em 0.125em rgba(0, 0, 0, 0.25)) drop-shadow(0em 0.062em 0.125em rgba(0, 0, 0, 0.25));
          filter: drop-shadow(0.062em 0.125em 0.125em rgba(0, 0, 0, 0.25)) drop-shadow(0em 0.062em 0.125em rgba(0, 0, 0, 0.25));
          overflow: hidden;
          -webkit-transition: var(--transition);
          -o-transition: var(--transition);
          transition: var(--transition);
        }}

        .theme-switch__moon {{
          -webkit-transform: translateX(100%);
          -ms-transform: translateX(100%);
          transform: translateX(100%);
          width: 100%;
          height: 100%;
          background-color: var(--moon-bg);
          border-radius: inherit;
          -webkit-box-shadow: 0.062em 0.062em 0.062em 0em rgba(254, 255, 239, 0.61) inset, 0em -0.062em 0.062em 0em #969696 inset;
          box-shadow: 0.062em 0.062em 0.062em 0em rgba(254, 255, 239, 0.61) inset, 0em -0.062em 0.062em 0em #969696 inset;
          -webkit-transition: var(--transition);
          -o-transition: var(--transition);
          transition: var(--transition);
          position: relative;
        }}

        .theme-switch__spot {{
          position: absolute;
          top: 0.75em;
          left: 0.312em;
          width: 0.75em;
          height: 0.75em;
          border-radius: var(--container-radius);
          background-color: var(--spot-color);
          -webkit-box-shadow: 0em 0.0312em 0.062em rgba(0, 0, 0, 0.25) inset;
          box-shadow: 0em 0.0312em 0.062em rgba(0, 0, 0, 0.25) inset;
        }}

        .theme-switch__spot:nth-of-type(2) {{
          width: 0.375em;
          height: 0.375em;
          top: 0.937em;
          left: 1.375em;
        }}

        .theme-switch__spot:nth-last-of-type(3) {{
          width: 0.25em;
          height: 0.25em;
          top: 0.312em;
          left: 0.812em;
        }}

        .theme-switch__clouds {{
          width: 1.25em;
          height: 1.25em;
          background-color: var(--clouds-color);
          border-radius: var(--container-radius);
          position: absolute;
          bottom: -0.625em;
          left: 0.312em;
          -webkit-box-shadow: 0.937em 0.312em var(--clouds-color), -0.312em -0.312em var(--back-clouds-color), 1.437em 0.375em var(--clouds-color), 0.5em -0.125em var(--back-clouds-color), 2.187em 0 var(--clouds-color), 1.25em -0.062em var(--back-clouds-color), 2.937em 0.312em var(--clouds-color), 2em -0.312em var(--back-clouds-color), 3.625em -0.062em var(--clouds-color), 2.625em 0em var(--back-clouds-color), 4.5em -0.312em var(--clouds-color), 3.375em -0.437em var(--back-clouds-color), 4.625em -1.75em 0 0.437em var(--clouds-color), 4em -0.625em var(--back-clouds-color), 4.125em -2.125em 0 0.437em var(--back-clouds-color);
          box-shadow: 0.937em 0.312em var(--clouds-color), -0.312em -0.312em var(--back-clouds-color), 1.437em 0.375em var(--clouds-color), 0.5em -0.125em var(--back-clouds-color), 2.187em 0 var(--clouds-color), 1.25em -0.062em var(--back-clouds-color), 2.937em 0.312em var(--clouds-color), 2em -0.312em var(--back-clouds-color), 3.625em -0.062em var(--clouds-color), 2.625em 0em var(--back-clouds-color), 4.5em -0.312em var(--clouds-color), 3.375em -0.437em var(--back-clouds-color), 4.625em -1.75em 0 0.437em var(--clouds-color), 4em -0.625em var(--back-clouds-color), 4.125em -2.125em 0 0.437em var(--back-clouds-color);
          -webkit-transition: 0.5s cubic-bezier(0, -0.02, 0.4, 1.25);
          -o-transition: 0.5s cubic-bezier(0, -0.02, 0.4, 1.25);
          transition: 0.5s cubic-bezier(0, -0.02, 0.4, 1.25);
        }}

        .theme-switch__stars-container {{
          position: absolute;
          color: var(--stars-color);
          top: -100%;
          left: 0.312em;
          width: 2.75em;
          height: auto;
          -webkit-transition: var(--transition);
          -o-transition: var(--transition);
          transition: var(--transition);
        }}

        /* actions */

        .theme-switch__checkbox:checked + .theme-switch__container {{
          background-color: var(--container-night-bg);
        }}

        .theme-switch__checkbox:checked + .theme-switch__container .theme-switch__circle-container {{
          left: calc(100% - var(--circle-container-offset) - var(--circle-container-diameter));
        }}

        .theme-switch__checkbox:checked + .theme-switch__container .theme-switch__circle-container:hover {{
          left: calc(100% - var(--circle-container-offset) - var(--circle-container-diameter) - 0.187em)
        }}

        .theme-switch__circle-container:hover {{
          left: calc(var(--circle-container-offset) + 0.187em);
        }}

        .theme-switch__checkbox:checked + .theme-switch__container .theme-switch__moon {{
          -webkit-transform: translate(0);
          -ms-transform: translate(0);
          transform: translate(0);
        }}

        .theme-switch__checkbox:checked + .theme-switch__container .theme-switch__clouds {{
          bottom: -4.062em;
        }}

        .theme-switch__checkbox:checked + .theme-switch__container .theme-switch__stars-container {{
          top: 50%;
          -webkit-transform: translateY(-50%);
          -ms-transform: translateY(-50%);
          transform: translateY(-50%);
        }}
        
        /* DARK MODE OVERRIDES */
        body.dark {{
            background: linear-gradient(142deg,rgba(0, 31, 33, 1) 0%, rgba(9, 95, 121, 1) 29%, rgba(30, 30, 45, 1) 57%, rgba(0, 42, 46, 1) 85%, rgba(0, 31, 33, 1) 100%);
            color: #eee;
        }}
        body.dark .header,
        body.dark .controls-panel,
        body.dark .chart-container {{
            background: rgba(30, 30, 45, 0.95);
            color: #eee;
        }}
        body.dark .checkbox-item label {{
            color: #f1f1f1;
        }}
        body.dark .stat-label {{
            color: #bbb;
        }}
        body.dark .reset-btn {{
            background: #003D4F;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(142deg,rgba(186, 233, 255, 1) 0%, rgba(0, 156, 204, 1) 29%, rgba(0, 0, 199, 1) 57%, rgba(0, 192, 209, 1) 85%, rgba(186, 233, 255, 1) 100%);
            min-height: 100vh;
            color: #333;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}

        .header {{
            text-align: center;
            margin-bottom: 30px;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }}

        .header h1 {{
            font-size: 2.5em;
            color: #2c3e50;
            margin-bottom: 10px;
            font-weight: 700;
        }}

        .header p {{
            color: #7f8c8d;
            font-size: 1.1em;
        }}

        .dashboard {{
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 30px;
            align-items: start;
        }}

        .controls-panel {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            height: fit-content;
            position: sticky;
            top: 20px;
        }}

        .control-group {{
            margin-bottom: 25px;
        }}

        .control-group h3 {{
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.1em;
            font-weight: 600;
        }}

        .checkbox-container {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .checkbox-item {{
            display: flex;
            align-items: center;
            padding: 8px 12px;
            border-radius: 10px;
            transition: all 0.3s ease;
            cursor: pointer;
            background: rgba(108, 92, 231, 0.05);
        }}

        .checkbox-item:hover {{
            background: rgba(108, 92, 231, 0.1);
            transform: translateX(5px);
        }}

        .checkbox-item input[type="checkbox"] {{
            margin-right: 10px;
            width: 18px;
            height: 18px;
            accent-color: #6c5ce7;
            cursor: pointer;
        }}

        .checkbox-item label {{
            cursor: pointer;
            font-weight: 500;
            color: #2d3436;
        }}

        .chart-container {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            height: 720px;
            position: relative;
        }}

        .chart-title {{
            text-align: center;
            margin-bottom: 20px;
            color: #2c3e50;
            font-size: 1.3em;
            font-weight: 600;
        }}
        
        body.dark .chart-title {{
            color: #ffffff;
        }}
        
        body.dark .header h1 {{
            color: #ffffff;
        }}
        
        body.dark .control-group h3 {{
            color: #ffffff;
        }}

        
        body.dark .header p {{
            color: #cccccc;
        }}


        .stats-bar {{
            display: flex;
            justify-content: space-around;
            margin-bottom: 20px;
            padding: 15px;
            background: rgba(108, 92, 231, 0.1);
            border-radius: 15px;
        }}

        .stat-item {{
            text-align: center;
        }}

        .stat-number {{
            font-size: 1.5em;
            font-weight: 700;
            color: #6c5ce7;
        }}

        .stat-label {{
            font-size: 0.9em;
            color: #636e72;
            margin-top: 5px;
        }}

        #chartCanvas {{
            border-radius: 15px;
        }}

        .no-data {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 400px;
            color: #636e72;
        }}

        .no-data-icon {{
            font-size: 4em;
            margin-bottom: 20px;
            opacity: 0.3;
        }}

        .reset-btn {{
            background: #009CCC;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
            width: 100%;
            margin-top: 20px;
        }}

        .reset-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(108, 92, 231, 0.3);
        }}

        @media (max-width: 768px) {{
            .dashboard {{
                grid-template-columns: 1fr;
                gap: 20px;
            }}

            .controls-panel {{
                position: static;
            }}

            .header h1 {{
                font-size: 2em;
            }}

            .chart-container {{
                height: 500px;
            }}
        }}

        /* Persian text support */
        .persian {{
            font-family: 'Tahoma', 'Arial', sans-serif;
            direction: rtl;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Course Frequency Analysis</h1>
            <label class="theme-switch">
              <input type="checkbox" class="theme-switch__checkbox" id="themeCheckbox">
              <div class="theme-switch__container">
                <div class="theme-switch__clouds"></div>
                <div class="theme-switch__stars-container">
                  <!-- SVG stays the same -->
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 144 55" fill="none">
                    <!-- truncated for brevity (you already have this part) -->
                  </svg>
                </div>
                <div class="theme-switch__circle-container">
                  <div class="theme-switch__sun-moon-container">
                    <div class="theme-switch__moon">
                      <div class="theme-switch__spot"></div>
                      <div class="theme-switch__spot"></div>
                      <div class="theme-switch__spot"></div>
                    </div>
                  </div>
                </div>
              </div>
            </label>

            <p>Interactive dashboard for analyzing course enrollment patterns across years and degree levels</p>
            <p><small>Generated from {len(rows)} course records across {len(all_years)} years and {len(all_degrees)} degree levels</small></p>
        </div>

        <div class="dashboard">
            <div class="controls-panel">
                <div class="control-group">
                    <h3>📅 Select Years</h3>
                    <div class="checkbox-container" id="yearCheckboxes">
                        <!-- Year checkboxes will be populated by JavaScript -->
                    </div>
                </div>

                <div class="control-group">
                    <h3>🎓 Select Degrees</h3>
                    <div class="checkbox-container" id="degreeCheckboxes">
                        <!-- Degree checkboxes will be populated by JavaScript -->
                    </div>
                </div>

                <button class="reset-btn" onclick="resetFilters()">🔄 Reset All Filters</button>
            </div>

            <div class="chart-container">
                <div class="chart-title" id="chartTitle">Course Frequency Analysis</div>

                <div class="stats-bar" id="statsBar">
                    <div class="stat-item">
                        <div class="stat-number" id="totalCourses">0</div>
                        <div class="stat-label">Total Courses</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number" id="totalEnrollments">0</div>
                        <div class="stat-label">Total Enrollments</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number" id="avgEnrollment">0</div>
                        <div class="stat-label">Avg per Course</div>
                    </div>
                </div>

                <div style="height: 500px; position: relative;">
                    <canvas id="chartCanvas"></canvas>
                    <div class="no-data" id="noDataMessage" style="display: none;">
                        <div class="no-data-icon">📊</div>
                        <h3>No Data Available</h3>
                        <p>Please select at least one year and one degree level to view the analysis.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Handle theme toggle checkbox
        const checkbox = document.getElementById('themeCheckbox');

        // Restore theme from localStorage
        document.addEventListener('DOMContentLoaded', function () {{
            initializeApp();

            const savedTheme = localStorage.getItem('preferredMode');
            if (savedTheme === 'dark') {{
                document.body.classList.add('dark');
                checkbox.checked = true;
            }}
        }});

        checkbox.addEventListener('change', function () {{
            if (checkbox.checked) {{
                document.body.classList.add('dark');
                localStorage.setItem('preferredMode', 'dark');
            }} else {{
                document.body.classList.remove('dark');
                localStorage.setItem('preferredMode', 'light');
            }}
        }});

        // Data loaded from your JSON file
        const rawData = {js_data};

        // Global variables
        let chart = null;
        let allYears = [];
        let allDegrees = [];
        let courseData = [];

        // Initialize the application
        function initializeApp() {{
            // Convert raw data to the format expected by the analysis
            courseData = [];
            const years = new Set();
            const degrees = new Set();

            rawData.forEach(item => {{
                const year = item.Year;
                const degree = item.Degree;
                years.add(year);
                degrees.add(degree);

                item.CourseList.forEach(course => {{
                    courseData.push({{
                        Year: year,
                        Degree: degree,
                        Course: course
                    }});
                }});
            }});

            allYears = Array.from(years).sort();
            const degreeOrder = [2, 4, 5];
            allDegrees = degreeOrder.filter(d => degrees.has(d));


            console.log('Data loaded:', {{
                totalRecords: courseData.length,
                years: allYears,
                degrees: allDegrees
            }});

            // Create checkboxes
            createYearCheckboxes();
            createDegreeCheckboxes();

            // Set default selections (matching your original Bokeh code)
            setDefaultSelections();

            // Initial chart update
            updateChart();
        }}

        function createYearCheckboxes() {{
            const container = document.getElementById('yearCheckboxes');
            container.innerHTML = '';

            allYears.forEach((year, index) => {{
                const div = document.createElement('div');
                div.className = 'checkbox-item';

                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.id = `year_${{year}}`;
                checkbox.value = year;
                // Default to checking the last year (index 5 in your original code)
                if (index === 3) checkbox.checked = true;
                checkbox.addEventListener('change', updateChart);

                const label = document.createElement('label');
                label.htmlFor = `year_${{year}}`;
                label.textContent = year;

                div.appendChild(checkbox);
                div.appendChild(label);
                container.appendChild(div);
            }});
        }}

        function createDegreeCheckboxes() {{
            const container = document.getElementById('degreeCheckboxes');
            container.innerHTML = '';

            // Degree mapping (matching your original labels)
            const degreeLabels = {{
                2: "کارشناسی (Bachelor)",
                4: "ارشد (Master)", 
                5: "دکتری (PhD)"
            }};

            allDegrees.forEach((degree, index) => {{
                const div = document.createElement('div');
                div.className = 'checkbox-item';

                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.id = `degree_${{degree}}`;
                checkbox.value = degree;
                // Default to checking first degree (index 0 in your original code)
                if (index === 0) checkbox.checked = true;
                checkbox.addEventListener('change', updateChart);

                const label = document.createElement('label');
                label.htmlFor = `degree_${{degree}}`;
                label.className = 'persian';
                label.textContent = degreeLabels[degree] || `Degree ${{degree}}`;

                div.appendChild(checkbox);
                div.appendChild(label);
                container.appendChild(div);
            }});
        }}

        function setDefaultSelections() {{
            // This function ensures default selections are set
            // (defaults are already set in createYearCheckboxes and createDegreeCheckboxes)
        }}

        function getSelectedYears() {{
            const checkboxes = document.querySelectorAll('#yearCheckboxes input[type="checkbox"]:checked');
            return Array.from(checkboxes).map(cb => parseInt(cb.value));
        }}

        function getSelectedDegrees() {{
            const checkboxes = document.querySelectorAll('#degreeCheckboxes input[type="checkbox"]:checked');
            return Array.from(checkboxes).map(cb => parseInt(cb.value));
        }}

        function getCourseCount(selectedYears, selectedDegrees) {{
            if (selectedYears.length === 0 || selectedDegrees.length === 0) {{
                return {{ courses: [], counts: [], years: [] }};
            }}

            console.log('Filtering with:', {{ selectedYears, selectedDegrees }});

            // Filter data (matching your original logic)
            const filtered = courseData.filter(row => 
                selectedYears.includes(row.Year) && selectedDegrees.includes(row.Degree)
            );

            console.log('Filtered records:', filtered.length);

            // Count courses
            const courseCounts = {{}};
            const courseYears = {{}};

            filtered.forEach(row => {{
                if (!courseCounts[row.Course]) {{
                    courseCounts[row.Course] = 0;
                    courseYears[row.Course] = new Set();
                }}
                courseCounts[row.Course]++;
                courseYears[row.Course].add(row.Year);
            }});

            // Sort by count (descending, matching your original logic)
            const sortedCourses = Object.entries(courseCounts)
                .sort((a, b) => b[1] - a[1]);

            if (sortedCourses.length === 0) {{
                return {{ courses: [], counts: [], years: [] }};
            }}

            const courses = sortedCourses.map(item => item[0]);
            const counts = sortedCourses.map(item => item[1]);
            const years = courses.map(course => 
                Array.from(courseYears[course]).sort().join(', ')
            );

            console.log('Course analysis result:', {{ 
                totalCourses: courses.length, 
                topCourse: courses[0], 
                topCount: counts[0] 
            }});

            return {{ courses, counts, years }};
        }}

        function updateChart() {{
            const selectedYears = getSelectedYears();
            const selectedDegrees = getSelectedDegrees();

            console.log('Updating chart with selections:', {{ selectedYears, selectedDegrees }});

            // Update title (matching your original format)
            const yearLabels = selectedYears.join(', ');
            const degreeLabels = selectedDegrees.map(d => {{
                switch(d) {{
                    case 1: return 'کارشناسی';
                    case 2: return 'ارشد';
                    case 3: return 'دکتری';
                    default: return d;
                }}
            }}).join(', ');

            document.getElementById('chartTitle').textContent = 
                `Course Frequency for Years: ${{yearLabels}} | Degrees: ${{degreeLabels}}`;

            const {{ courses, counts, years }} = getCourseCount(selectedYears, selectedDegrees);

            if (courses.length === 0) {{
                showNoData();
                return;
            }}

            hideNoData();
            updateStats(courses, counts);
            renderChart(courses, counts, years);
        }}

        function updateStats(courses, counts) {{
            const totalCourses = courses.length;
            const totalEnrollments = counts.reduce((sum, count) => sum + count, 0);
            const avgEnrollment = totalCourses > 0 ? Math.round(totalEnrollments / totalCourses) : 0;

            document.getElementById('totalCourses').textContent = totalCourses;
            document.getElementById('totalEnrollments').textContent = totalEnrollments;
            document.getElementById('avgEnrollment').textContent = avgEnrollment;
        }}

        function renderChart(courses, counts, years) {{
            const ctx = document.getElementById('chartCanvas').getContext('2d');

            if (chart) {{
                chart.destroy();
            }}

            // Generate colors for bars
            const colors = courses.map((_, i) => {{
                const hue = (i * 137.508) % 360; // Golden angle approximation
                return `hsla(${{hue}}, 70%, 60%, 0.8)`;
            }});

            const borderColors = courses.map((_, i) => {{
                const hue = (i * 137.508) % 360;
                return `hsla(${{hue}}, 70%, 50%, 1)`;
            }});

            chart = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: courses,
                    datasets: [{{
                        label: 'Frequency',
                        data: counts,
                        backgroundColor: colors,
                        borderColor: borderColors,
                        borderWidth: 2,
                        borderRadius: 8,
                        borderSkipped: false,
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            display: false
                        }},
                        tooltip: {{
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: 'white',
                            bodyColor: 'white',
                            borderColor: '#6c5ce7',
                            borderWidth: 1,
                            cornerRadius: 10,
                            displayColors: false,
                            callbacks: {{
                                label: function(context) {{
                                    const index = context.dataIndex;
                                    return [
                                        `Frequency: ${{context.parsed.y}}`,
                                        `Years: ${{years[index]}}`
                                    ];
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            ticks: {{
                                maxRotation: 45,
                                minRotation: 45,
                                font: {{
                                    size: 10
                                }}
                            }},
                            grid: {{
                                display: false
                            }}
                        }},
                        y: {{
                            beginAtZero: true,
                            ticks: {{
                                stepSize: 1
                            }},
                            grid: {{
                                color: 'rgba(0, 0, 0, 0.1)'
                            }}
                        }}
                    }},
                    animation: {{
                        duration: 1000,
                        easing: 'easeOutQuart'
                    }}
                }}
            }});
        }}

        function showNoData() {{
            document.getElementById('chartCanvas').style.display = 'none';
            document.getElementById('noDataMessage').style.display = 'flex';
            document.getElementById('totalCourses').textContent = '0';
            document.getElementById('totalEnrollments').textContent = '0';
            document.getElementById('avgEnrollment').textContent = '0';
        }}

        function hideNoData() {{
            document.getElementById('chartCanvas').style.display = 'block';
            document.getElementById('noDataMessage').style.display = 'none';
        }}

        function resetFilters() {{
            // Uncheck all checkboxes
            document.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);

            // Set default selections (matching original Bokeh defaults)
            if (allYears.length > 0) {{
                const defaultYearCheckbox = document.getElementById(`year_403`);
                if (defaultYearCheckbox) defaultYearCheckbox.checked = true;
            }}

            if (allDegrees.length > 0) {{
                const defaultDegreeCheckbox = document.getElementById(`degree_${{allDegrees[0]}}`);
                if (defaultDegreeCheckbox) defaultDegreeCheckbox.checked = true;
            }}

            // Update chart
            updateChart();
        }}

        // Initialize the app when the page loads
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('DOM loaded, initializing app...');
            initializeApp();
        }});
        function toggleDarkMode() {{
            document.body.classList.toggle('dark');
        }}

    </script>
</body>
</html>'''

    # Write the HTML file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Successfully generated {output_path}")
        print(f"Data summary: {len(rows)} course records, {len(all_years)} years, {len(all_degrees)} degree levels")
        print(f"Years: {all_years}")
        print(f"Degrees: {all_degrees}")
        return True
    except Exception as e:
        print(f"Error writing HTML file: {e}")
        return False


if __name__ == "__main__":
    DATA_PATH = os.getcwd() + "\\Data\\data.json"
    OUTPUT_PATH = "index.html"

    print("Generating HTML dashboard...")
    success = generate_html_dashboard(DATA_PATH, OUTPUT_PATH)

    if success:
        print(f"Dashboard generated successfully!")
        print(f"Open {OUTPUT_PATH} in your browser to view the dashboard")
        print(f"You can now upload this file to GitHub Pages or any web host")
    else:
        print("Failed to generate dashboard")