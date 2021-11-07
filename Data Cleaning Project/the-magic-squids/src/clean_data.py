import os
import pandas as pd
from pandas._libs.tslibs.timestamps import Timestamp
from pandas.core.dtypes.dtypes import DatetimeTZDtype
import pytz
from functools import lru_cache
from collections import Counter
from difflib import SequenceMatcher
from datetime import datetime, timedelta

# Gets us one level up, so that we can access all files
os.chdir(os.path.relpath('..'))

# Hard coding which columns need to have their types corrected, and to what type
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

# Hard coding what columns need to be reconciled with what other tables, and the columns that need to match from each
reconciliation = {
	'trr_trr_refresh': {

		'data_officer': [('officer_last_name', 'last_name'),
						 ('officer_first_name', 'first_name'), ('officer_birth_year', 'birth_year'), 
						 ('officer_race', 'race'), 
						 ('officer_gender', 'gender'), ('officer_appointed_date', 'appointed_date')],

		'trr_trr': [('subject_race', 'subject_race'), 
					('subject_gender', 'subject_gender'), ('subject_birth_year', 'subject_birth_year'),
					('party_fired_first', 'party_fired_first'),
					('indoor_or_outdoor', 'indoor_or_outdoor'),
					('location', 'location'),
					('street', 'street')]		
	},

	'trr_trr_subjectweapon_refresh': {

		'trr_trr_subjectweapon' : [('weapon_type', 'weapon_type')]
	},

	'trr_trrstatus_refresh': {

		'data_officer': [('officer_first_name', 'first_name'),
						  ('officer_last_name', 'last_name'),
						  ('officer_birth_year', 'birth_year'),
						  ('officer_race', 'race'),
						  ('officer_gender', 'gender'),
						  ('officer_appointed_date', 'appointed_date')]
	}
}

def clean_print(p, last=False):
	print(p, end='\r', flush=True)
	if last: print()

# Returns a CPDB table as a dataframe
@lru_cache
def load_data(filename, clean=False):

	# Can include the .csv or not when inputting filename
	filename = filename + '.csv' if '.csv' not in filename else filename
	filename = 'SELECT_FROM_' + filename if 'SELECT_FROM_' not in filename else filename

	# Fetching the data
	try:
		return pd.read_csv('./raw-data/' + filename, low_memory=False)

	# Data not found
	except FileNotFoundError:
		raise FileNotFoundError(f'Unable to find data for \'{filename}\'. Please ensure that ensure that all tables have been downloaded correctly from datagrip, and that all filenames in the raw-data folder begin with \'SELECT_FROM_\'')


# Given a set of valid values and a set of values to convert, returns a dictionary where keys are values to be converted, and values are the respective appropriate conversion
def conversion_dict(valid, to_convert):

	conversions = {}

	# We want a valid conversion value for every possible type of value in the refresh data
	for value in to_convert:

		# If value is already a valid value
		if value in valid:
			conversions[value] = value

		# Perform string similarity matching between refresh value and valid values
		else:
			best = ''
			best_ratio = 0
			for valid_value in valid:

				# Ensuring we perform string comparisons
				valid_value, value = str(valid_value), str(value)

				# We want ensure that single characters are compared to single characters, otherwise matches become nondeterministic
				if len(value) == 1 or len(valid_value) == 1:
					refresh_value, valid_value = value[0], valid_value[0]
				else:
					refresh_value = value
				
				# Perform the comparison
				ratio = SequenceMatcher(None, refresh_value.lower(), valid_value.lower()).ratio()

				# Compare it to the current best
				if ratio > best_ratio:
					best = valid_value
					best_ratio = ratio
				if best_ratio > 0.95:
					break

			# If the best ratio is not above 0.3, use NULL instead
			conversions[value] = best if best_ratio > 0.3 else float('NaN')

	return conversions


# Given a string of one or more words, returns a string with all words capitalized, and otherwise lowercase. Performs itself recursively for lists
def capitalized(string):

	# Handle lists of strings that need capitalization
	if isinstance(string, list):
		return [capitalized(x) for x in string]

	# Only return a capitalized string if we are handling a string
	return ' '.join([x.lower().capitalize() for x in string.split()]) if isinstance(string, str) else string


# Given an ambiguous integer corresponding to age or birth year, returns the most likely birth year
def age_to_year(age, split=1940):

	# Handle list of ages recursively:
	if isinstance(age, list):
		return [age_to_year(x) for x in age]
	
	# Guessing their birth year based on a split
	if age != float('NaN') and age < 100:
		split = 2021 - split
		return age + 1900 if age > split else 2021 - age

	# Correctly formatted ages and non number values
	return age


# If a date is after 2021, return the same datetime in 1900s
def fix_dates(date):

	# Converting strings to datetime objects
	if isinstance(date, str):
		date = datetime.fromisoformat(date)

	# Getting UTC localized today date
	utc = pytz.UTC
	today = utc.localize(datetime.today())

	# Condition for changing the date
	if isinstance(date, (pd.DatetimeTZDtype, datetime)) and date > today:
		return date - timedelta(days=36500)

	return date


# Cleans floats / NaN values for final CSV output
def clean_float(f):
	if f.endswith('.0'):
		return f[:-2]
	elif f == 'nan':
		return ''
	return f

# Cleans strings w/ NaN values for final CSV output
def clean_string(s):
	if s == 'nan':
		return ''
	return s


# Taking a pd.Series object and a conversion dict / function, returns a new series with all values converted accordingly. SERIES MUST BE A SINGLE COLUMN
def convert(series, cd):

	# Capitalizing values by default
	if isinstance(cd, type(lambda: None)):
		for i, value in enumerate(series):
			series.at[i] = cd(value)

	# Using a conversion dict
	elif isinstance(cd, dict):
		for i, value in enumerate(series):
			series.at[i] = cd[value]

	return series


def match_officer(row, index, length, officers = load_data('data_officer')):

	print(f'Currently identifying officer for TRR {index} / {length}', end='\r', flush=True)

	# Getting a dictionary of all the relevant values for matching
	match_columns = ['officer_last_name', 'officer_first_name', 'officer_appointed_date', 'officer_birth_year', 'officer_race', 'officer_gender', 'officer_middle_initial']

	# Getting the data cleaned to match with the data_officer
	row_data = {}
	for column in match_columns:
		row_data[column] = str(row[column])[:10] if isinstance(row[column], (pd.DatetimeTZDtype, datetime, Timestamp)) else row[column]

	
	# Initializing query to contain only the info we need to search through
	query = officers[['id', 'last_name', 'first_name', 'appointed_date', 'birth_year', 'race', 'gender', 'middle_initial']]

	# Going through all the row data to identify the officer
	for row, data in row_data.items():

		# We want to skip NaNs
		if data == float('NaN'):
			continue

		# Removing 'officer_'
		row = row[8:]

		# Updating the query with the new row data
		new = query[query[row] == data]

		if new.empty:
			continue

		query = new

		if len(query) == 1:
			return query.iat[0, 0]

	# We did not identify a single officer
	return float('NaN')
	


# Given a filename, outputs a cleaned CSV of the file in ../output/
def clean_data(filename):

	# Fetching table
	data = load_data(filename)

	# Removing 'SELECT_FROM_' and '.csv'
	name = filename[12:-4]
	print(f'Currently cleaning {name}')

	# 2.1: Correcting types
	if name in type_correction:

		clean_print(f'correcting types...')

		for column in type_correction[name]:

			# Correcting datetimes
			if column[1] == 'datetime64':
				#print(data[column[0]])
				data[column[0]] = pd.to_datetime(data[column[0]], utc=True, errors='coerce')
				#print(data[column[0]])

			# Correcting integers
			elif column[1] == 'int64':
				#data[column[0]] = pd.to_numeric(data[column[0]], errors='coerce').fillna(0).astype('int')
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
	if name in reconciliation:

		clean_print(f'reconciling data...')

		for table in reconciliation[name]:
			
			# Getting the real data (already cleaned)
			clean = load_data(table)

			for column in reconciliation[name][table]:

				# Getting all valid conversion values
				valid = set(clean[column[1]].to_list())
				dtype = Counter([type(x) for x in valid]).most_common()[0][0]

				if isinstance(data[column[0]].dtype, pd.DatetimeTZDtype):
					#print(data[column[0]])
					data[column[0]] = convert(data[column[0]], fix_dates)
					#print(data[column[0]])

				# Reconciliation of numerical columns
				elif isinstance(dtype, (int, float)):
					data[column[0]] = convert(data[column[0]], age_to_year)

				# Reconciliation of categorical columns
				elif len(valid) < 50:

					# All values which need a conversion
					to_clean = set(data[column[0]].to_list())

					# Finding conversions between values
					cd = conversion_dict(valid, to_clean)

					# Setting new series in place of the old column
					data[column[0]] = convert(data[column[0]], cd)

				# Reconciliation of non-categorical columns
				else:
					data[column[0]] = convert(data[column[0]], capitalized)


	# 3.1 Linking Officer IDs
	if name in ('trr_trr_refresh', 'trr_trrstatus_refresh'):

		clean_print(f'linking officer IDs...')

		# Gathering officer IDs per TRR
		data['officer_id'] = None
		limit = -1
		limit = limit if limit >= 0 else len(data)

		for i in range(limit):
			data.at[i, 'officer_id'] = match_officer(data.iloc[i], i, len(data))
		print()

		data['officer_id'] = data['officer_id'].astype(float)

		# Removing columns that are not present in the final tables
		data.drop(['officer_first_name', 'officer_middle_initial', 'officer_last_name', 'officer_race', 'officer_gender', 'officer_birth_year', 'officer_appointed_date'], axis=1, inplace=True)

		if name == 'trr_trr_refresh':
			data.drop('officer_unit_detail', axis=1, inplace=True)


	# 3.2 Linking police units
	if name == 'trr_trr_refresh':

		clean_print(f'linking police units...')

		# Getting associations between unit names and their ID
		cd = {'REDACTED': float('NaN')}
		policeunits = load_data('data_policeunit')
		for _, row in policeunits.iterrows():
			cd[str(row['unit_name'])] = row['id']
		
		# Changing unit names to unit IDs
		data['officer_unit_name'] = convert(data['officer_unit_name'], cd)
		data.rename({'officer_unit_name': 'officer_unit_id'}, axis=1, inplace=True)
		data['officer_unit_detail_id'] = data['officer_unit_id'][:]


	# 3.3 Valdating TRR IDs
	else:

		clean_print(f'validating TRR IDs...')
		
		# Getting all valid TRR ids
		valid_trrs = set([x for x in load_data('trr_trr_refresh')['id']])

		# Finding which TRR ids to drop
		to_drop = []
		for index, row in data.iterrows():
			clean_print(f'validating TRR id {index + 1} / {len(data)}')
			if row['trr_report_id'] not in valid_trrs:
				to_drop.append(index)

		# Dropping rows which contain invalid TRR IDs
		clean_print(f'\ndropped {len(to_drop)} rows containing invalid TRR IDs', last=True)
		data.drop(to_drop, inplace=True)


	# Cleaning floats before final CSV output
	for c in data.columns:
		data[c] = convert(data[c].astype(str), clean_float) if data[c].dtype in [int, float] else (convert(data[c], clean_string) if data[c].dtype != float else data[c])

	# Outputting all cleaned tables to ./output/ as CSVs
	clean_print(f'outputting to CSV...')
	data.to_csv('./output/' + name + '.csv', index=False)

	# Final Output
	clean_print(f'cleaning of {name} complete!\n', last=True)
	return data, name


if __name__ == '__main__':

	# Grabbing all CSV files that need to be cleaned
	# Sometimes datagrip fails to include 'h' in 'refresh'... not sure what's going on here.
	to_clean = [f for f in os.listdir('./raw-data/') if 'refres' in f]

	# Creating a cleaned version for each
	for f in to_clean:
		data, name = clean_data(f)
