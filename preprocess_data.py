import numpy as np
import pandas as pd        # For loading and processing the dataset
from sklearn.model_selection import train_test_split
import csv
from math import *
import plotly.plotly as py
import plotly.tools as tls
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly.io as pio

PLAN_TYPES = [0, 30, 365]
# load the data
FILENAME = 'metro-bike-share-trip-data.csv'
data = pd.read_csv(FILENAME)

services = len(data[data['Ending Station ID'] == 3000]['Ending Station ID'])

# drop unfixable and incomplete entries, as well as service repair entries
data = data.dropna(thresh=13)
data = data[data['Ending Station ID'] != 3000]
data = data.reset_index(drop=True)

# number of rows in the data
entries = len(data['Duration'])

# create entries for year, month, day, hour, minute
data['Start Year'] = data['Start Time'].apply(lambda x: int(str(x)[:4])) 
data['Start Month'] = data['Start Time'].apply(lambda x: int(str(x)[5:7]))
data['Start Day'] = data['Start Time'].apply(lambda x: int(str(x)[8:10]))
data['Start Hour'] = data['Start Time'].apply(lambda x: int(str(x)[11:13]))
data['Start Minute'] = data['Start Time'].apply(lambda x: int(str(x)[14:16]))

data['End Year'] = data['End Time'].apply(lambda x: int(str(x)[:4])) 
data['End Month'] = data['End Time'].apply(lambda x: int(str(x)[5:7]))
data['End Day'] = data['End Time'].apply(lambda x: int(str(x)[8:10]))
data['End Hour'] = data['End Time'].apply(lambda x: int(str(x)[11:13]))
data['End Minute'] = data['End Time'].apply(lambda x: int(str(x)[14:16]))

# distance column using Haversine Formula

# fill in coordinates for entries with ID's but blank coordinates
loc_map = {} # maps ID to coordinates
missing_coords = [[], []] # entries to be fixed

for i in range(entries):
	try: # starting 
		[1 / float(data['Starting Station Latitude'][i]), 1 / float(data['Starting Station Longitude'][i])] # catch any 0 - blank spaces for lat/long
		loc_map[int(data['Starting Station ID'][i])] = [data['Starting Station Latitude'][i], data['Starting Station Longitude'][i]]
	except:
		missing_coords[0].append(i)
	
	try: # ending
		[1 / float(data['Ending Station Latitude'][i]), 1 / float(data['Ending Station Longitude'][i])]  # catch any 0 - blank spaces for lat/long
		loc_map[int(data['Ending Station ID'][i])] = [data['Ending Station Latitude'][i], data['Ending Station Longitude'][i]]
	except:
		missing_coords[1].append(i)

# fix the blank or 0 coordinate entries
for i in missing_coords[0]:
	data['Starting Station Latitude'][i] = loc_map[int(data['Starting Station ID'][i])][0]
	data['Starting Station Longitude'][i] = loc_map[int(data['Starting Station ID'][i])][1]

for i in missing_coords[1]:
	data['Ending Station Latitude'][i] = loc_map[int(data['Ending Station ID'][i])][0]
	data['Ending Station Longitude'][i] = loc_map[int(data['Ending Station ID'][i])][1]		

	
# calculate distances for each trip using the Haversine formula

R = 6373.0

distances = []
for i in range(entries):
	lat1, lat2 = data['Starting Station Latitude'][i], data['Ending Station Latitude'][i]
	lon1, lon2 = data['Ending Station Longitude'][i], data['Ending Station Longitude'][i]
	lat1, lat2, lon1, lon2 = radians(lat1), radians(lat2), radians(lon1), radians(lon2)
	dlon = lon2 - lon1
	dlat = lat2 - lat1
	a = (sin(dlat/2)) ** 2 + cos(lat1) * cos(lat2) * (sin(dlon/2)) ** 2
	c = 2 * atan2(sqrt(a), sqrt(1-a))
	distances.append(R * c)

data['Net Distance'] = np.array(distances)

# earliest and latest entries
earliest, latest = min(data['Start Time']), max(data['End Time'])
print(earliest, latest)
# frequency that each location is used for starting/ending trip

#starting
unique, counts = np.unique(data['Starting Station ID'], return_counts=True)
freq_start = dict(zip(unique, counts))

#ending
unique, counts = np.unique(data['Ending Station ID'], return_counts=True)
freq_end = dict(zip(unique, counts))

# most popular starting and ending locations
print(max(freq_start, key = lambda x: freq_start[x]))
print(max(freq_end, key = lambda x: freq_end[x]))

# distance statistics
valids = data.loc[data['Net Distance'].notnull()]['Net Distance']
min_dist, max_dist = min(valids), max(valids)
avg_dist = sum(valids) / len(valids)

# split by year
d_2016, d_2017 = data[data['Start Year'] == 2016], data[data['Start Year'] == 2017]

# split by month
split_data = []
for i in [d_2016, d_2017]:
	split_data.append([i[i['Start Month'] == x] for x in range(1, 13)])

#split by day, and then hour
for i in range(len(split_data)):
	month_count = 0
	for j in split_data[i]:
		split_data[i][month_count] = [j[j['Start Day'] == x] for x in range(1, 32) if len(j[j['Start Day'] == x]) != 0]
		day_count = 0
		for k in split_data[i][month_count]:
			split_data[i][month_count][day_count] = [k[k['Start Hour'] == x] for x in range(0, 24)]
			day_count += 1
		month_count += 1

# hourly ride data available by using split_data[yr][month][day][hour]

# statistics generator
daily_stats = [] # count of rides per day
hourly_stats = [0 for i in range(24)] # number of total rides for each of the 24 hours
seasonal_type_stats = [[0, 0, 0] for i in range(4)] # seasons are periods of 3 months, data is [one-time, monthly, annual]
split_counts, day_counts = split_data[:], split_data[:] # count of rides by hour, count of rides by day
for yr in range(len(split_data)):
	sub1 = split_data[yr]
	for mth in range(len(sub1)):
		sub2 = sub1[mth]
		for day in range(len(sub2)):
			sub3 = sub2[day]
			for hour in range(len(sub3)):
				sub4 = sub3[hour]
				count = len(sub4['Start Minute'])
				split_counts[yr][mth][day][hour] = count
				hourly_stats[hour] += count
				# seasonal stats
				for i in range(len(PLAN_TYPES)):
					seasonal_type_stats[int(mth/3)][i] += len(sub4[sub4['Plan Duration'] == PLAN_TYPES[i]])
			daily_stats.append(sum(split_counts[yr][mth][day]))
			day_counts[yr][mth][day] = sum(split_counts[yr][mth][day])

# average number of riders daily
v_daily = [i for i in daily_stats if i]
avg_riders_daily = sum(v_daily) / len(v_daily)

# regular users (and average)
reg_data = data[data['Plan Duration'] != 0]
print(len(reg_data['Plan Duration'])/len(v_daily))

valid_ridetimes = data[data['Ending Station ID'] != 3000]['Duration']
avg_ride_time = sum(valid_ridetimes) / len(valid_ridetimes)
print(avg_ride_time, avg_riders_daily)
print(entries, avg_dist)
print(day_counts)





trace2 = go.Bar(x = np.arange(len(daily_stats)), y=daily_stats)
dt1 = [trace2]
layout1 = go.Layout(xaxis=dict(autorange=True, title = "Day"), yaxis=dict(autorange=True, title = "Number of Rides"))

fig5 = go.Figure(data=dt1, layout=layout1)
py.image.save_as({'data': fig5}, 'static/img/fig4.png')


# reorder seasons so that they go in chronological order
seasonal_type_stats = [seasonal_type_stats[2], seasonal_type_stats[3], seasonal_type_stats[0]]

x = ['Summer 2016', 'Fall 2016', 'Winter 2017']
y = [[seasonal_type_stats[i][j] for i in range(3)] for j in range(3)]
y_labels = ['One-Time', 'Monthly', 'Annual']
trace = [0 for i in range(3)]
for i in range(3):
	trace[i] = go.Bar(x=x,y=y[i],text=y[i],textposition = 'auto', name = y_labels[i],\
		marker=dict(color=('rgb(%d,200,225)'%(158-50*i)), line=dict(color=\
			'rgb(8,48,107)',width=1.5),),opacity=0.6)

dt = [i for i in trace]
py.image.save_as({'data': dt}, 'static/img/fig5.png')

x_ = ['Bike Returned to Same Station', 'Bike Returned to Different Station', 'Service Repair']

no_net_count = len(data[data['Net Distance'] == 0]['Net Distance'])
y_ = [no_net_count, entries - no_net_count, services]
trace7 = [go.Bar(x_ = x, y=y_, text = y_, textposition = 'auto',\
 marker=dict(color='rgb(158,202,225)',line=dict(color='rgb(8,48,107)'\
 	,width=1.5),),opacity=0.6)]
py.image.save_as({'data': trace7}, 'static/img/fig6.png')
# export data
#data.to_csv('out.csv')