# HOW TO RUN OUR CODE

Before beginning, please install our dependencies by running the following command within your terminal/shell within a fresh python env:
- pip install -r requirements.txt

Open our SQL code with datagrip, and highlight all statements. Then, right click the highlighted selection and click 'execute to file', choosing the-magic-squids/raw-data as the output directory. This should output 14 total files - one for each query (6 normal and 6 refresh, + data_officer and data_policeunit).

To create clean CSV files, simply run clean_data.py. It will output 6 cleaned tables as CSV files to the-magic-squids/output/
