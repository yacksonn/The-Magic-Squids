# Preparation

Create a fresh python environment then activate it. Navigate to the path containing our code (checkpoint-5/src/). Install our requirements using the following command:

 - pip install -r requirements.txt

All instructions henceforth should be performed from inside the src directory

# Instructions (WITH GPU)

The instructions below **REQUIRE** a CUDA GPU. If you do not have a GPU available locally, please follow the second set of instructions available below the first

Please run the following command, entering 'DataSci4AI' when prompted for a password:

 - bash run.txt

If this command wont work or you wish to access the database in a different way, our workflow can be recreated by using the following commands in sequence

 - postgres < queries.txt (these queries need to be run in order to generate our data csvs. You can use whatever method you prefer to access the files in this step, as long as you end up with pop_raw.csv and narratives.csv in the ../data/ directory)
 - python prep_data.py (this should produce two new csvs in the data folder, 'population.csv' and 'sentiments.csv')
 - python analyze_data.py (this will produce our final output)

In case you are unable to produce any of the CSVs in the steps prior to the last, they have been provided by default in the data folder.

If you really prefer to run this locally without a GPU, it can be done by removing the device=0 argument on line 28 of prep_data.py. This will allow prep_data.py to run through without issue even if torch has not been compiled with CUDA enabled. Expect execution times in excess of 30 minutes.

# Instructions (WITHOUT GPU)

Please follow this set of instructions if you do not have access to a GPU locally.

Run the following commands (or perform the necessary actions) sequentially:

 - psql -U cpdbstudent -h codd04.research.northwestern.edu -p 5433 postgres < queries.txt (use password 'DataSci4AI'. This can be replaced with any database access method you prefer, as long as the postgres database gets queried with the queries in queries.txt)
 - Go to [the following google colab notebook](https://colab.research.google.com/drive/1bZVZNMksCV82z-WJHVFC4PDKRkUB-9oW?usp=sharing) (requires Northwestern email)
 - Upload the csv files 'pop_raw.csv' and 'narratives.csv' available in the checkpoint-5/data/ directory
 - Run both cells (execution time is ~3 minutes)
 - Download newly generated csvs 'sentiments.csv' and 'population.csv' on the left to the checkpoint-5/data/ directory
 - python analyze_data.py (this will produce our final output)

In case you are unable to produce any of the CSVs in the steps prior to the last, they have been provided by default in the data folder.
