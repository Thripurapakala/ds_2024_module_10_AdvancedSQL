# Import the dependencies.

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt
import numpy as np

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Declare a Base using `automap_base()`
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
# /
# /api/v1.0/precipitation
# /api/v1.0/stations
# /api/v1.0/temp/<start>
# /api?v1.0/temp/<start>/<end>

@app.route("/")
def welcome():
    
    return (
        f"Welcome to the Hawaii Climate Analysis API:"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitaion/<br/>"
        f"/api/v1.0/stations/<br/>"
        f"/api/v1.0/tobs/<br/>"
        f"/api/v1.0/temp/start/<br/>"
        f"/api/v1.0/temp/start/end/<br/>"
        f"<p> 'start' and 'end' date should be int he format MMDDYYYY.</p>"
    )
# SQL Queries
@app.route("/api/v1.0/precipitation/")
def precipitation():
    "Return the data for the last year precipitaion"
    pre_year = dt.date(2017, 8 , 23) - dt.timedelta(days=365)
    #last year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= pre_year).all()

    session.close()
    #Dict with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)


@app.route("/api/v1.0/stations/")
def stations():
    "get list of stations"
    results= session.query(Station.station).all()

    session.close()
    #results into a array and conver to a list
    stations = list(np.ravel(results))
    return jsonify(stations=stations)


@app.route("/api/v1.0/tobs/")
def temp_monthly():
    #one year ago
    pre_year = dt.date(2017, 8 , 23) - dt.timedelta(days=365)
    #last year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= pre_year).all()
    #stations for all tobs from the last yeat
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= pre_year).all()
    session.close()
    #results array and convert to a list
    temp = list(np.ravel(results))
    return jsonify(temp = temp)

@app.route("/api/v1.0/temp/<start>/")
@app.route("/api/v1.0/temp/<start>/<end>/")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""

    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:

        start = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()

        session.close()

        temps = list(np.ravel(results))
        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and stop
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps=temps)


if __name__ == '__main__':
    app.run()