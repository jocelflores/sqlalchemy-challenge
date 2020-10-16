import numpy as np
import os

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
     """Return a list of the date and precipitation values"""

    # Query all dates and precipitation
     session = Session(engine)
     results = session.query(measurement.date, measurement.prcp).all()

     # close the session to end the communication with the database
     session.close()

     # Convert list of tuples into normal list
     all_precip = []
     for precip in results:
        precip_dict = {(precip.date):precip.prcp}
        all_precip.append(precip_dict)

     return jsonify(all_precip)

@app.route("/api/v1.0/stations")
def stations():
     """Return a list of stations"""

     # Open a communication session with the database
     session = Session(engine)

     # Query all stations
     results = session.query(station.station).all()

     # close the session to end the communication with the database
     session.close()

     station_list = list(np.ravel(results))
     print(station_list)
     return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
     """Return a list of the most active station, dates and temperatures"""

     # Open a communication session with the database
     session = Session(engine)

     # Query all stations, dates and temperatures
     query = session.query(measurement.station, func.count(measurement.tobs)).group_by(measurement.station).order_by(func.count(measurement.tobs).desc()).all()
     results = session.query(measurement.station, measurement.date, measurement.tobs).filter(measurement.date > '2016-08-23', measurement.station == query[0][0]).all()

     # close the session to end the communication with the database
     session.close()

     active_station = list(np.ravel(results))
     print(active_station)
     return jsonify(active_station)

@app.route("/api/v1.0/<start>")
def dates(start):
    #grab temperatures 
        
    search_term = start

    session = Session(engine)
    results = session.query(func.avg(measurement.tobs), func.max(measurement.tobs), func.min(measurement.tobs)).filter(measurement.date > search_term).group_by(measurement.date).first()
    return jsonify(results)

@app.route("/api/v1.0/<start>/<end>")
def startend(start,end):
    #grab temperatures in range
        
    search_term1 = start
    search_term2 = end
    session = Session(engine)
    results = session.query(func.avg(measurement.tobs), func.max(measurement.tobs), func.min(measurement.tobs)).filter(search_term2 > measurement.date, measurement.date > search_term1).group_by(measurement.date).first()
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
