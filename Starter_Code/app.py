# Import the dependencies.



#################################################
# Database Setup
#################################################


# reflect an existing database into a new model

# reflect the tables


# Save references to each table


# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################

from flask import Flask, jsonify
from sqlalchemy import create_engine, func, inspect
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import numpy as np

# Create a Flask app
app = Flask(__name__)

# Create SQLAlchemy engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Define the homepage route
@app.route('/')
def homepage():
    """Homepage route"""
    return (
        f"<h1>Welcome to Your Flask API!</h1>"
        f"<h2>Available Routes:</h2>"
        f"<ul>"
        f"<li><a href='/api/v1.0/precipitation'>Precipitation data for the last year</a></li>"
        f"<li><a href='/api/v1.0/stations'>List of weather stations</a></li>"
        f"<li><a href='/api/v1.0/tobs'>Temperature data for the last year</a></li>"
        f"<li>/api/v1.0/&lt;start&gt; - Min, Avg, and Max temperatures from start date</li>"
        f"<li>/api/v1.0/&lt;start&gt;/&lt;end&gt; - Min, Avg, and Max temperatures for a date range</li>"
        f"</ul>"
    )

# Define the route to get precipitation data for the last year
@app.route('/api/v1.0/precipitation')
def precipitation():
    """Return precipitation data for the last year as JSON"""
    session = Session(engine)
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date - timedelta(days=365)
    precipitation_data = session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date >= one_year_ago)\
        .order_by(Measurement.date).all()
    session.close()
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    return jsonify(precipitation_dict)

# Define the route to get a list of weather stations
@app.route('/api/v1.0/stations')
def stations():
    """Return a list of weather stations as JSON"""
    session = Session(engine)
    stations = session.query(Station.station).all()
    session.close()
    station_list = [station[0] for station in stations]
    return jsonify(station_list)

# Define the route to get temperature data for the last year
@app.route('/api/v1.0/tobs')
def tobs():
    """Return temperature data for the last year from the most active station as JSON"""
    session = Session(engine)
    most_active_station = session.query(Measurement.station)\
        .group_by(Measurement.station)\
        .order_by(func.count(Measurement.station).desc()).first()[0]
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date - timedelta(days=365)
    temperature_data = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == most_active_station)\
        .filter(Measurement.date >= one_year_ago)\
        .order_by(Measurement.date).all()
    session.close()
    temperature_dict = {date: tobs for date, tobs in temperature_data}
    return jsonify(temperature_dict)

# Define the route to get temperature statistics for a given start date
@app.route('/api/v1.0/<start>')
def temp_stats_start(start):
    """Return temperature statistics from a start date to the last date as JSON"""
    session = Session(engine)
    start_date = datetime.strptime(start, '%Y-%m-%d')
    temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start_date).all()
    session.close()
    temp_stats_list = list(np.ravel(temp_stats))
    return jsonify(temp_stats_list)

# Define the route to get temperature statistics for a given date range
@app.route('/api/v1.0/<start>/<end>')
def temp_stats_range(start, end):
    """Return temperature statistics for a date range as JSON"""
    session = Session(engine)
    start_date = datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.strptime(end, '%Y-%m-%d')
    temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start_date)\
        .filter(Measurement.date <= end_date).all()
    session.close()
    temp_stats_list = list(np.ravel(temp_stats))
    return jsonify(temp_stats_list)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)


#################################################
# Flask Routes
#################################################
