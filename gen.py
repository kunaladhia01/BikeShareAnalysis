import numpy as np
import pandas as pd        # For loading and processing the dataset
from sklearn.model_selection import train_test_split
import csv
import plotly.plotly as py
import plotly.tools as tls
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly.io as pio
#import geoplotlib
from math import *
days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
PLAN_TYPES = [0, 30, 365]

# list of location IDs excluding 3000 (this list was generated from preprocess_data.py)
locs = sorted([3014, 3016, 3032, 3021, 3054, 3022, 3076, 3005, 3031, 3078,\
 3047, 3063, 3042, 3030, 3018, 3006, 3033, 3007, 3037, 3068, 3034, 3019,\
  3052, 3040, 3066, 3036, 3053, 3065, 3035, 3028, 3055, 3058, 3051, 3038,\
   3075, 3067, 3049, 3062, 3020, 3045, 3080, 3056, 3079, 3008, 3069, 3060,\
    3029, 3023, 3074, 3026, 3025, 3057, 3027, 3077, 3059, 3010, 3064, 3046,\
     3011, 3048, 3081, 3024, 3082, 4108, 3000, 3009, 3039])


def check_date(year, month, day):
	if year == 2016 and (month > 7 or month == 7 and day > 6) or (year == 2017 and month < 4):
		if day <= days[month-1]:
			return True
	return False


def generate_visuals(y, m, d):
	# load and split data
	data = pd.read_csv('out.csv')
	data = data[data['Start Year'] == y]
	data = data[data['Start Month'] == m]
	data = data[data['Start Day'] == d]
	hourly = [data[data['Start Hour'] == x] for x in range(24)]

	# extract statistics
	stat_counts = [len(hourly[i]['Start Hour']) for i in range(24)]
	plan_dist = [[hourly[i][hourly[i]['Plan Duration'] == PLAN_TYPES[j]] for j in range(3)] for i in range(24)]
	dist_counts = [[len(plan_dist[i][j]['Plan Duration']) for j in range(3)] for i in range(24)]

	# plot for hourly stats by passholder type
	ind = np.arange(24)
	width = 0.5
	mpl_fig = plt.figure()
	ax = mpl_fig.add_subplot(111)
	p1 = ax.bar(ind, [dist_counts[i][0] for i in ind], width, color=(0.2588,0.4433,1.0))
	p2 = ax.bar(ind, [dist_counts[i][1] for i in ind], width, color=(1.0,0.5,0.62),
	             bottom=[dist_counts[i][0] for i in ind])
	p3 = ax.bar(ind, [dist_counts[i][2] for i in ind], width, color=(0.33,0.33,0.33),
	             bottom=[dist_counts[i][1] for i in ind])
	ax.set_ylabel('Number of Rides')
	ax.set_xlabel('Hour')
	ax.set_title('Number of Rides by Passholder Type per Hour')

	ax.set_xticks(ind)
	ax.set_yticks(np.arange(0, max(stat_counts) + 5, 10))
	ax.set_xticklabels(('G1', 'G2', 'G3', 'G4', 'G5'))

	plotly_fig = tls.mpl_to_plotly( mpl_fig )

	plotly_fig["layout"]["showlegend"] = True
	plotly_fig["data"][0]["name"] = "One-Time"
	plotly_fig["data"][1]["name"] = "Monthly"
	plotly_fig["data"][2]["name"] = "Annual"

	py.image.save_as({'data': plotly_fig}, 'static/img/fig1.png')

	# plot for amount of bikes entering and leaving 15 most active stations

	# gather data
	locs1 = locs[:]
	lfreqs = [[len(data[data['Starting Station ID'] == i]['Starting Station ID']),\
	 len(data[data['Ending Station ID'] == i]['Ending Station ID'])] for i in locs]

	# determine 15 most popular spots
	for i in range(15):
		lc = lfreqs.index(max(lfreqs[i:], key = sum))
		lfreqs, locs1 = [lfreqs.pop(lc)] + lfreqs, [locs1.pop(lc)] + locs1
	lfreqs, locs1 = lfreqs[:15][::-1], locs1[:15][::-1]

	# create plot
	trace1 = go.Bar(x=["ID: " + str(i) for i in locs1], y=[i[0] for i in lfreqs], name ='Starting Location')
	trace2 = go.Bar(x=["ID: " + str(i) for i in locs1], y=[i[1] for i in lfreqs], name ='Ending Location')
	dt = [trace1, trace2]
	layout = go.Layout(barmode='group', xaxis = dict(title = "Starting Location ID"), yaxis = dict(title = "Number of Rides"))
	fig = go.Figure(data=dt, layout=layout)
	py.image.save_as({'data': fig}, 'static/img/fig2.png')
	

	# plot for number of rides by duration, not including servicing
	new_data = data[data['Ending Station ID'] != 3000]
	dur_freq = [len(new_data[new_data['Duration'] // 60 == i]['Duration']) for i in range(60*24)]
	print(dur_freq)
	# group by 30 - minute intervals
	dur_freq = [sum(dur_freq[30*i:30*(i+1)]) for i in range(48)]
	# drop unnecessary and outlier end values
	while dur_freq[-1] == 0 or dur_freq.count(0) > 5:
		dur_freq.pop()
	print(dur_freq)

	trace2 = go.Bar(x=[str(30*i)+" to "+str(30*(i+1)) for i in range(len(dur_freq))], y=dur_freq)
	dt1 = [trace2]
	layout1 = go.Layout(xaxis=dict(autorange=True, title = "Duration Interval (Minutes)"), yaxis=dict(type='log', autorange=True, title = "Number of Rides"))

	fig2 = go.Figure(data=dt1, layout=layout1)
	py.image.save_as({'data': fig2}, 'static/img/fig3.png')





