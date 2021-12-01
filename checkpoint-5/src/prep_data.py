from collections import Counter
from transformers import pipeline
from math import log
import pandas as pd

#  -- CLEANING THE POPULATION TABLE --
pop_raw = pd.read_csv('../data/pop_raw.csv')

# Our population table
population  = pd.DataFrame(columns=['district_id', 'district_name', 'Black', 'White', 'Native American', 'Other', 'Hispanic', 'Asian', 'Total'])

# Getting all valid district ids and district names
population['district_id'] = sorted(set([y for y in Counter(pop_raw['area_id'])]))
population['district_name'] = population['district_id'].map(lambda x: pop_raw[pop_raw['area_id'] == x].iloc[0, 3])

# Getting population values
for race in population.columns[2:8]:
	population[race] = population['district_id'].map(lambda x: pop_raw[pop_raw['area_id'] == x][pop_raw['race'] == race].iloc[0, 1])
for index, row in population.iterrows():
	population.at[index, 'Total'] = sum(row[2:8].tolist())

population.to_csv('../data/population.csv')


# -- GETTING SENTIMENT FOR CR_TEXT --

# Getting our sentiment analyzer and data
sentiment = pipeline('sentiment-analysis', device=0)
narratives = pd.read_csv('../data/narratives.csv', dtype={"crid": "int", "cr_text": "string", "cr_location": "string", "district_id": "int"})

# Cleaning our narratives before sentiment analysis
to_remove = ['Initial / Intake', 'Allegation', 'Finding', '(None Entered)']

def clean(narrative):

	def is_empty(string):
		if not string:
			return True
		else:
			for character in string:
				if character != ' ':
					return False
			return True

	def is_narrative(string):
		for x in to_remove:
			if string.startswith(x):
				return False
		return True


	# Splitting for each new text entry
	narrative = [x.strip() for x in narrative.split(':')]

	# Cleaning each text entry
	narrative = list(set([(' '.join(x.split('\n')[:-1]) if '\n' in x else x) for x in narrative]))

	# Ensuring that the size of each entry is below 512 tokens
	narrative = [' '.join(text.split()[:400]) for text in narrative]

	# Removing entries that are not entries
	return [x.strip() for x in narrative if is_narrative(x) and not is_empty(x)]

narratives['cr_text'] = narratives['cr_text'].map(clean)


# Getting the sentiment scores for each cleaned narrative
def get_sentiment(cr_text):

	def sentiment_score(sentiment):
		return log(1 - sentiment['score']) * (-1 if sentiment['label'] == 'POSITIVE' else 1)

	scores = [sentiment_score(sentiment(text)[0]) for text in cr_text]

	if not scores:
		return float('nan')

	return round(sum(scores) / len(scores), 2)

narratives['sentiment'] = narratives['cr_text'].map(get_sentiment)
narratives = narratives[narratives['sentiment'] != float('nan')]

narratives.to_csv('../data/sentiments.csv')
