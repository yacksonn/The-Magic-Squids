import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy import stats as scipystats

# Importing data
population = pd.read_csv('../data/population.csv')
population = population[population.columns[1:]]
sentiments = pd.read_csv('../data/sentiments.csv')
sentiments = sentiments[sentiments.columns[1:]]

# Our new dataframe containing our analysis results
df = pd.DataFrame(columns=['id', 'name', 'black', 'white', 'asian', 'native_american', 'hispanic', 'other', 'sentiment'])

df['id'] = population['district_id']
df['name'] = population['district_name']

for row_index, row in df.iterrows():
	for column_index in range(2, 8):
		proportion = population.iat[row_index, column_index] / population.iat[row_index, 8]
		df.iat[row_index, column_index] = proportion


# Calculating average sentiment for each district
averages = {x: [] for x in df['id']}

for index, row in sentiments.iterrows():
	averages[row['district_id']].append(row['sentiment'])

# Gathering stats for statistical analysis
stats = {k: {'std': np.std(v), 'mean': sum(v) / len(v), 'samples': v, 'n': len(v)} for k, v in averages.items()}

df['sentiment'] = [x['mean'] for x in stats.values()]
df['sentiment_std'] = [x['std'] for x in stats.values()]
df['nsamples'] = [x['n'] for x in stats.values()]

df.to_csv('../data/analysis.csv')

# Allows us to easily plot sentiment against any race variable
def getxy(column):
	data = [(x, y) for x, y in zip(df[column], df['sentiment'])]
	data.sort(key=lambda x: x[0])

	x = [datum[0] for datum in data]
	y = [datum[1] for datum in data]

	return x, y

'''
plt.plot(*getxy('white'))
plt.plot(*getxy('black'))
plt.show()
'''

pop_raw = pd.read_csv('../data/pop_raw.csv')

# Given a race, performs a 
def anova(race, num_groups=3):

	# Dividing the districts into 3 groups of roughly equal size
	group_size = sum(df['nsamples']) / num_groups

	race_stats = df[[race, 'id', 'sentiment' , 'sentiment_std', 'nsamples']].sort_values(race)

	district_groups = {str(x): [] for x in range(1, num_groups + 1)}

	index = 0
	for group in district_groups:
		n = 0
		while n < group_size:

			# We wont be able to completely fill the last group
			if len(stats) < index + 1:
				break

			# Adding the district to that group, incrementing samples
			district_groups[group].append(race_stats.iat[index, 1])
			n += race_stats.iat[index, 4]
			index += 1

	# Getting the total race porportion for each group
	group_race_proportions = {}

	for group_num, group in district_groups.items():
		total_pop = sum([sum(pop_raw[pop_raw['area_id'] == d_id]['count']) for d_id in group])
		total_race = sum([pop_raw[pop_raw['area_id'] == d_id][pop_raw['race'] == race.capitalize()]['count'].item() for d_id in group])
		group_race_proportions[group_num] = {race: total_race, 'total': total_pop, 'proportion': round(total_race / total_pop, 5)}

	# Getting all samples / stats per group
	district_groups = {k: [sample for d_id in v for sample in stats[d_id]['samples']] for k, v in district_groups.items()}

	groups = list(district_groups.values())

	district_groups = {k: {'std': np.std(v), 'mean': sum(v) / len(v), 'n': len(v)} for k, v in district_groups.items()}

	for group_num, group in district_groups.items():
		group[f'{race}_pop'] = group_race_proportions[group_num][race]
		group['total_pop'] = group_race_proportions[group_num]['total']
		group['proportion'] = group_race_proportions[group_num]['proportion'] 

	return scipystats.f_oneway(*groups), district_groups


test_race = 'hispanic'

p, groups = anova(test_race)

x = [v['proportion'] for v in groups.values()]
y = [v['mean'] for v in groups.values()]

plt.plot(x, y)
plt.show()

print(f'{test_race.capitalize()} groups are statistically different with {round(100 - (p.pvalue * 100), 4)}% confidence, p = {round(p.pvalue, 4)}')

