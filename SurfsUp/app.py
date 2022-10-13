# 1. import Flask
from flask import Flask, jsonify
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc, and_

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
conn = engine.connect()
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)
first_date = session.query(Measurement).\
    order_by(desc(Measurement.date)).\
    first().date
startDate = (dt.datetime.strptime(first_date,"%Y-%m-%d") - dt.timedelta(days=365)).strftime("%Y-%m-%d")
session.close()
print("Finished Setup")

# 2. Create an app, being sure to pass __name__
app = Flask(__name__)


# 3. Define what to do when a user hits the index route
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return "Available Routes:<br>/api/v1.0/precipitation<br>/api/v1.0/stations<br>/api/v1.0/tobs<br>/api/v1.0/&lt;start&gt;<br>/api/v1.0/&LT;start&GT;/&LT;end&GT;"


# 4. Define what to do when a user hits the /about route
@app.route("/api/v1.0/precipitation")
def precipitation():
    engine = create_engine("sqlite:///Resources/hawaii.sqlite")
    conn = engine.connect()
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    Measurement = Base.classes.measurement
    Station = Base.classes.station

    session = Session(engine)
    first_date = session.query(Measurement).\
        order_by(desc(Measurement.date)).\
        first().date
    startDate = (dt.datetime.strptime(first_date,"%Y-%m-%d") - dt.timedelta(days=365)).strftime("%Y-%m-%d")
    



    print("Server received request for 'Preciptiation' page...")
    scores = session.query(Measurement).\
        filter(Measurement.date >= '2016-08-23').\
        filter(Measurement.prcp >= 0).\
        with_entities(Measurement.date,Measurement.prcp)
    results = pd.read_sql(scores.statement,conn).set_index("date").to_dict()
    print(jsonify(results))
    session.close()
    return jsonify(results)
    

@app.route("/api/v1.0/stations")
def stations():
    engine = create_engine("sqlite:///Resources/hawaii.sqlite")
    conn = engine.connect()
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    Measurement = Base.classes.measurement
    Station = Base.classes.station

    stations = session.query(Station)
    results = pd.read_sql(stations.statement,conn).set_index("station").to_dict("index")
    session.close()
    return(jsonify(results))

@app.route("/api/v1.0/tobs")
def tobs():
    engine = create_engine("sqlite:///Resources/hawaii.sqlite")
    conn = engine.connect()
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    Measurement = Base.classes.measurement
    Station = Base.classes.station

    station_activity = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).order_by(desc(func.count(Measurement.station)))
 
    most_active_id = station_activity.first()[0]



    tobs_results = session.query(Measurement).\
        with_entities(Measurement.date,Measurement.tobs).\
        filter(Measurement.station == most_active_id).\
        filter(Measurement.date >= '2016-08-23')
    results = pd.read_sql(tobs_results.statement,conn).set_index("date").to_dict()
    session.close()
    return(jsonify(results))

@app.route("/api/v1.0/<start>")
def records_since(start):
    engine = create_engine("sqlite:///Resources/hawaii.sqlite")
    conn = engine.connect()
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    Measurement = Base.classes.measurement
    Station = Base.classes.station

    temps = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).first()

    results = {"TMIN": temps[0],
        "TAVG": temps[1],
        "TMAX": temps[2]}
    session.close()
    return(jsonify(results))

@app.route("/api/v1.0/<start>/<end>")
def records_betwixt(start,end):
    engine = create_engine("sqlite:///Resources/hawaii.sqlite")
    conn = engine.connect()
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    Measurement = Base.classes.measurement
    Station = Base.classes.station

    temps = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(and_(Measurement.date >= start,\
        Measurement.date <= end)).first()

    results = {"TMIN": temps[0],
        "TAVG": temps[1],
        "TMAX": temps[2]}
    session.close()
    return(jsonify(results))



if __name__ == "__main__":
    app.run(debug=True)
