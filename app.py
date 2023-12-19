# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import numpy as np

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route('/')
def welcome():
    return (
        f"Welcome!<br/>"
        f"Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    #calc date 1 year from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #query data for last year
    precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()
    session.close()
    #dict comprehension
    precip = {date: prcp for date, prcp, in precipitation}
    return jsonify(precip)

@app.route('/api/v1.0/stations')
def stations():
    #return list of stations
    result = session.query(Station.station).all()
    session.close()

    #unravel results
    result = list(np.ravel(result))
    return jsonify(result)

@app.route('/api/v1.0/tobs')
def temp_monthly():
    #calc date 1 year from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= prev_year).\
        filter(Measurement.station == 'USC00519281').all()
    session.close()
    #unravel results
    results = list(np.ravel(results))
    return jsonify(results)

@app.route('/api/v1.0/temp/<start>')
@app.route('/api/v1.0/temp/<start>/<end>')
def stats(start, end=None):
    #select statement
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]

    if not end:
        start = dt.datetime.strptime(start, "%m%d%Y")

        result = session.query(*sel).\
            filter(Measurement.date >= start).all()
        
        session.close()

        temps = list(np.ravel(result))
        return jsonify(temps)

    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")
    
    result = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    session.close()

    temps = list(np.ravel(result))
    return jsonify(temps)

if __name__ == '__main__':
    app.run()