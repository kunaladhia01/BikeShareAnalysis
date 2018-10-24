from flask import Flask, render_template, request, redirect
from gen import generate_visuals, check_date
from flask_cachebuster import CacheBuster
import sys,os

app = Flask(__name__)
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']


config = { 'extensions': ['.js', '.css', '.csv','.png'], 'hash_size': 5 }
cache_buster = CacheBuster(config=config)
cache_buster.init_app(app)


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

			dtstr = str(year) + str(month) + str(day) + '.png'

			# check if day is within parameters
			if check_date(year, month, day):
				generate_visuals(year, month, day)
				date = MONTHS[month - 1] + " " + str(day) + ", " + str(year)
				print("EFGH")
				return redirect('/daily-stats/' + date + '/' + dtstr)
			else:
				return render_template('index.html', message = "No data available for this day.")

		except Exception as e:
			print (str(e))
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)

			try:
				station = int(redr)

			except:
				return render_template('index.html', message = "Invalid Search!")

	return render_template('index.html')
 
@app.route("/daily-stats/<string:date>/<string:dtstr>", methods=['post', 'get'])
def stats(date,dtstr):
	print(date)
	return render_template('ind_stats.html', message = date, fig111 = 'img/fig111' + dtstr, fig222 = 'img/fig222' + dtstr, fig333 = 'img/fig333' + dtstr)


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
