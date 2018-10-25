Steps for installing project:

1. git clone https://github.com/kunaladhia01/CapitalOne.git
2. virtualenv capenv --python=python3
3. source capenv/bin/activate
4. cd CapitalOne
5. pip install -r requirements.txt​

Instructions for configuring plot.ly

1. Visiting https://plot.ly/python/getting-started/ for setting up ploty.ly API account
2.  Activate virtualenv and invoke python shell
3. Issue following command on python shell
    import plotly
    plotly.tools.set_credentials_file(username='userid', api_key=APIKey')
    
    
    
The site addresses all of the required deliverables, as well as the first and last optional questions, on the main page. The second optional question is incorporated into an additional bonus feature I added to the web app (located at the bottom of the homepage), which allows the user to enter any date from 07/07/2016 to 03/31/2017 (the span of the data set). The app will then generate three additional visuals for the specified date in slideshow format in a new page:

-Number of rides by pass-holder type per hour

-Number of rides starting and ending at the 15 most active bike stations for the day (the net change addresses optional question #2)

-Number of rides by trip duration, split into 30-minute intervals

Some notes:

1. preprocess_data.py: processes the raw data and creates the images seen on the homepage

2. app.py: the main application file, with form handling, rendering, and exception handling

3. gen.py: functions for validity of form data and generating an individual day's graphs



In general:

1. The site may load for a bit (up to 5-10 seconds) once a date is entered and submitted at the bottom of the homepage because of the time it takes to process the data and generate the visuals, along with server-side speed limitations.

2. Please don't try out too many different dates! The Plotly account used to generate the graphs is a trial account, meaning only 100 graphs can be created per 24 hour period (so 33 different dates can be tested within a day).

3. There are many (seemingly unnecessary) blocks of code for cache busting, a well-known issue with Flask. These steps (like the filenames for images) are necessary to overcome this issue.
