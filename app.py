import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement

Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

# Import Flask
from flask import Flask, jsonify

# Create an app
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

# Define what to do when a user hits the index route
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>")



#Define what to do when a user hits the /api/v1.0/precipation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for the 'precipitation' page...")
    # Create a session to the database 
    session = Session(engine)

    # Find the most recent date in the data set (2 ways to do it)
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    latest_date
    # Starting from the most recent data point in the database. 
    # Calculate the date one year from the last date in data set.
    year = int(latest_date[0][:4])
    month = int(latest_date[0][5:7])
    day = int(latest_date[0][8:10])

    query_date = dt.date(year, month, day) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    prcp_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date>=query_date).all()

    session.close()

    prcp_tuple = list(np.ravel(prcp_data))

    return jsonify(prcp_tuple)   


#Define what to do when a user hits the /api/v1.0/stations route
@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for the 'stations' page...")
    # Create a session to the database 
    session = Session(engine)

    stations_list = session.query(Measurement.station).\
    group_by(Measurement.station).all()
    
    session.close()

    stations_tuple = list(np.ravel(stations_list))

    return jsonify(stations_tuple) 


#Define what to do when a user hits the /api/v1.0/tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for the 'tobs' page...")
    # Create a session to the database 
    session = Session(engine)
    
    station_count = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()

    #Create Pandas DataFrame of query
    station_df = pd.DataFrame(columns = ['Station', 'Frequency'])
    for row in station_count:
        station_df = station_df.append({'Station':row[0],'Frequency':row[1]}, ignore_index=True)

    #Most active station
    most_active_station = station_df.iloc[0,0]
    
    tobs_list = session.query(Measurement.station, Measurement.tobs).\
    filter(Measurement.station == most_active_station).all()

    session.close()

    tobs_tuple = list(np.ravel(tobs_list))

    return jsonify(tobs_tuple) 

if __name__ == "__main__":
    app.run(debug=True)