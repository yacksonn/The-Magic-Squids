import os
import pandas as pd
from collections import Counter

# Gets us one level up, so that we can access all files
os.chdir(os.path.relpath('..'))

# Hard coding which tables need to be altered
type_correction = {
	'trr_trr_refresh': [('trr_datetime', 'datetime64'),
						('beat', 'int64'),
						('officer_appointed_date', 'datetime64'),
						('officer_birth_year', 'int64'),
						('officer_age', 'int64'),
						('officer_on_duty', 'bool'),
						('officer_injured', 'bool'),
						('officer_in_uniform', 'bool'),
						('subject_birth_year', 'int64'),
						('subject_age', 'int64'),
						('subject_armed', 'bool'),
						('subject_injured', 'bool'),
						('subject_alleged_injury', 'bool'),
						('notify_oemc', 'bool'),
						('notify_district_sergeant', 'bool'),
						('notify_op_command', 'bool'),
						('notify_det_division', 'bool'),
						('trr_created', 'datetime64')
						],
	'trr_weapondischarge_refresh': [('firearm_reloaded', 'bool'),
									('sight_used', 'bool')
									],
	'trr_weapondischarge_refres': [('firearm_reloaded', 'bool'),
								   ('sight_used', 'bool')
								   ],
	'trr_trrstatus_refresh': [('officer_appointed_date', 'datetime64'),
							  ('officer_birth_year', 'int64'),
							  ('status_datetime', 'datetime64')
							  ]

}

reconciliation = { }

# Returns an uncleaned table as a dataframe
def load_data(filename):
	return pd.read_csv('./raw-data/' + filename, low_memory=False)


# Given a filename, outputs a cleaned CSV of the file in ../output
def clean_data(filename):
	data = load_data(filename)

	# Removing 'SELECT_FROM_' and '.csv'
	name = filename[12:-4]

	# 2.1: Correcting types
	if name in type_correction:
		for column in type_correction[name]:

			# Correcting datetimes
			if column[1] == 'datetime64':
				data[column[0]] = pd.to_datetime(data[column[0]], utc=True, errors='coerce')

			# Correcting integers
			elif column[1] == 'int64':
				data[column[0]] = pd.to_numeric(data[column[0]], errors='coerce', downcast='integer')

			# Correcting bools
			else:
				for i in range(len(data)):
					item = data.at[i, column[0]]
					if isinstance(item, str):
						data.at[i, column[0]] = item.lower()[0] == 'y'
					elif isinstance(item, bool):
						continue
					else:
						data.at[i, column[0]] = None

	# 2.2: Reconciliation

	return data, name



if __name__ == '__main__':

	# Grabbing all CSV files
	to_clean = [f for f in os.listdir('./raw-data') if f[-4:] == '.csv']

	# Creating a cleaned version for each
	for f in to_clean:
		data, name = clean_data(f)
		if name == 'trr_trr_refresh': 
			pass
