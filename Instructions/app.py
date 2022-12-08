#Dependencies
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify, request
import datetime as dt
from sqlalchemy import desc
from sqlalchemy import asc





#################################################
# Database Setup
#################################################

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#define base
Base=automap_base()
# reflect an existing database into a new model
Base.prepare(autoload_with=engine)

# Save references to each table
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
    """List all available api routes"""
    return(
        f"Below are the available paths<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation ():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date one year from the last date in data set.
    year_delta_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    year_data = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date > year_delta_date).\
        order_by(measurement.date).all()

    #close session
    session.close()

    # Save the query results as a Pandas DataFrame and set the index to the date column
    year_data_df = pd.DataFrame(year_data, columns =['Date', 'Precipitation_Score']).set_index('Date')
    year_dict=year_data_df.to_dict()

    return jsonify(year_dict)

@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Design a query to show the name of each station in the dataset
    Stations_name = session.query(station.name).distinct().all()
    station_names = pd.DataFrame(Stations_name)
    station_dict = station_names.to_dict()

    #close session
    session.close()

    return jsonify(station_dict)

@app.route("/api/v1.0/tobs")
def tobs():

     # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find the most recent date of the most active station
    rd = session.query(measurement.date).filter(measurement.station == 'USC00519281').\
    order_by(desc(measurement.date)).first()
    #rd results in 2017-08-18
    

    # Calculate the date one year from the lastest, most active station, date.
    year_delta_date = dt.date(2017, 8, 18) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    year_data = session.query(measurement.date, measurement.tobs).\
    filter(measurement.date > year_delta_date).\
    order_by(measurement.date).all()

    # convert date and percipitation data to dictionary where 
    year_data_df = pd.DataFrame(year_data)
    year_data_dict = year_data_df['tobs'].to_dict()

    return jsonify(year_data_dict)

     #close session
    session.close()

@app.route("/api/v1.0/start")
def start():

     # Create our session (link) from Python to the DB
    session = Session(engine)

    #select start date 11/21/2015, and end date 12/12/2015
    start_date = dt.date(2015, 11, 21)
    end_date = dt.date(2016, 12, 12)

    #Start date station min, avg, max temp
    Start_date_min= session.query(func.min(measurement.tobs)).filter(measurement.date == start_date).all()
    Start_date_avg =session.query(func.avg(measurement.tobs)).filter(measurement.date == start_date).all()
    Start_date_max = session.query(func.max(measurement.tobs)).filter(measurement.date == start_date).all()                          

    # Calculate the date one year from the lastest, most active station, date.
    date = dt.date(2015, 11, 21) - dt.timedelta(days=365)

    #for dates greater than 11/21/2015 return the date, min, avg, and max
    dates_info = session.query(measurement.date, func.min(measurement.tobs),func.avg(measurement.tobs),\
    func.max(measurement.tobs)).group_by(measurement.date).filter(measurement.date >= start_date).all()
    dates_info_df = pd.DataFrame(dates_info).to_dict( 'records')
    #above code returns requested information, I cant find where we went over conferting multiple columns for the josonify, it will not let me pass a the dictionary with more than one column.

    #find same info for a range of dates.
    dates_range = session.query(measurement.date, func.min(measurement.tobs),func.avg(measurement.tobs),\
    func.max(measurement.tobs)).group_by(measurement.date).filter(measurement.date >= start_date).\
    filter(measurement.date <= end_date).all()
    dates_info_range_df = pd.DataFrame(dates_range).to_dict( 'records')
    #above code returns requested information, I cant find where we went over conferting multiple columns for the josonify, it will not let me pass a the dictionary with more than one column.


    return (
        f"On 11/21/2015 the minimum, avg, and max temp was {Start_date_min } {Start_date_avg } {Start_date_max}."
        f"{jsonify(dates_info_df)}"
        f"{jsonify(dates_info_range_df)}"

    #close session
    session.close()

if __name__ == '__main__':
    app.run(debug=True)
