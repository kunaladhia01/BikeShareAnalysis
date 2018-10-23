from flask import Flask, render_template, request, redirect
from gen import generate_visuals, check_date
from flask_cache_buster import CacheBuster

app = Flask(__name__)
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

@app.route("/",  methods=['post', 'get'])
def index():
	message = ''
	if request.method == 'POST':
		redr = request.form.get('spec')
		print(redr)
		try:
			month = int(redr[:2])
			day = int(redr[3:5])
			year = int(redr[6:10])
			# check if day is within parameters
			if check_date(year, month, day):
				generate_visuals(year, month, day)
				date = MONTHS[month - 1] + " " + str(day) + ", " + str(year)
				print("EFGH")
				return redirect('/daily-stats/' + date)
			else:
				return render_template('index.html', message = "No data available for this day.")

		except:
			try:
				station = int(redr)

			except:
				return render_template('index.html', message = "Invalid Search!")

	return render_template('index.html')
 
@app.route("/daily-stats/<string:date>", methods=['post', 'get'])
def stats(date):
	print(date)
	return render_template('ind_stats.html', message = date)


# No caching at all for API endpoints.
@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0' 
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response
if __name__ == "__main__":
	app.run()

