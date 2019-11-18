### Import necessary items to run queries. Take from Jupyter Notebook. ###

# Basic Python Dependencies 
import numpy as np
import pandas as pd
import datetime as dt

# SQLAlchemy Dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#Create engine. (I always put reference files into the same folder/directory as my program; it simplifies things.)
engine = create_engine("sqlite:///hawaii.sqlite", connect_args={'check_same_thread':False})
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB

connection = engine.connect()




last_date = 2017-8-23
year_ago = dt.date(2017, 8, 23) - dt.timedelta(days = 365)

##################################################################
#########################FLASK APP################################
##################################################################

# Import dependencies 

from flask import Flask, jsonify

# Create the app
climate_app = Flask(__name__)

# Define a method for the home page.
@climate_app.route("/")

def home(): 
    return(
    f"Welcome home!</br>"
    f"Here are the available routes:</br>"
    f"</br>"
    f"To see precipitation data, visit: /api/v1.0/precipitation</br>"
    f"</br>"
    f"To see station data, visit: /api/v1.0/stations</br>"
    f"</br>"
    f"For temperature observaton data, go to: /api/v1.0/tobs</br>"
    f"</br>"
    f"To look at data since a date in the past: /api/v1.0/&ltyyyy-mm-dd&gt</br>"
    f"Above path will return minimum, average, and maximum temperatures based on all available dates since date provided</br>"
    f"</br>"
    f"To look at data within a range: /api/v1.1/&ltyyyy-mm-dd&gt/&ltyyyy-mm-dd&gt</br>"
    f"Above path will return minimum, average, and maximum temperatures based on all available dates between dates provided</br>"
    )

    
# Define method for "precipitation" route
# Convert query results to a Dictionary using date as the key and prcp as the value. 
# Return the jsonified representation as the results. 


#Establish route. 
@climate_app.route("/api/v1.0/precipitation")
def precipitation():
    """Goal is to return a dictionary with precipitation data"""
#Create a session.     
    session=Session(engine)
#Run query to get precipitation data for the past last year of data available    
    year_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>=year_ago).group_by(Measurement.date).order_by(Measurement.date).all()
#Close session
    session.close()
#Create an empty variable for your data
    year_precipitation = []
#Loop through the query results. 
#Create an empty dictionary. Set the date from your query results as the key and the precipitation as the value.
#Append the dictionary entry to the empty variable you set outside of the loop.
    for record in year_data:
        yr_prcp_dict={}
        yr_prcp_dict[record.date] = record.prcp 
        year_precipitation.append(yr_prcp_dict)
#Return the jsonified list of pairs. 
    return(jsonify(year_precipitation))
    
 
# Define method for "stations" route
# Return a jsonified list of the stations. I chose to use the station id number, as it was the value in the "station" column.    
 
@climate_app.route("/api/v1.0/stations")
def stations():
    
    session=Session(engine)
    
    stations = session.query(Measurement.station).group_by(Measurement.station).all()
    
    session.close()
    
    station_list = list(np.ravel(stations))
    
    return(jsonify(station_list))


# Define method for "tobs" route
# Query for dates and temperatures for previous year
# Return a JSON list of temperatures and dates
# As above, so below. 
@climate_app.route("/api/v1.0/tobs")
def tobs():
#Code
    session=Session(engine)
    
    year_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date>=year_ago).group_by(Measurement.date).order_by(Measurement.date).all()
    
    session.close()
    
    year_temperature = []

    for tobs_record in year_tobs:
        yr_tobs_dict={}
        yr_tobs_dict[tobs_record.date] = tobs_record.tobs 
        year_temperature.append(yr_tobs_dict)

    return jsonify(year_temperature)
    
    
# Define method for "start" route
# Query for minimum, average, and maximum temperature for dates greater than/equal to provided date
# Return (brace yourself) jsonified list

@climate_app.route("/api/v1.0/<start>")
def start(start):    
    
    session=Session(engine)
    
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    
    session.close()
    
    start_list = []
    for startresult in temp_data:
        startresult_dict = {}
        startresult_dict['Lowest Temperature']=startresult[0]
        startresult_dict['Average Temperature']=startresult[1]
        startresult_dict['Maximum Temperature']=startresult[2]
        start_list.append(startresult_dict)
        
    return jsonify(start_list)
    
    
    
    # Define method for "start/end" route
# Query for minimum, average, and maximum temperature for dates within range inclusive
# Return (brace yourself) jsonified list


@climate_app.route("/api/v1.0/<start>/<end>")
def range_enclosed(start, end):
    
    session=Session(engine)
    
    startend = session.query(Measurement.date, func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    session.close()
    
    startend_list = []
    for result in startend:
        result_dict = {}
        result_dict['Lowest Temperature']=result[3]
        result_dict['Average Temperature']=result[1]
        result_dict['Maximum Temperature']=result[2]
        startend_list.append(result_dict)
        
    return jsonify(startend_list)
        
    
if __name__=="__main__":
    climate_app.run(debug="True")