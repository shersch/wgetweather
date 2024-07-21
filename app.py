from flask import Flask, request, render_template, redirect
from dotenv import load_dotenv, find_dotenv
import requests
import geocoder
import os
from prettytable import PrettyTable
import logging
import pytz
from datetime import datetime
from random import randrange
import const as c

logging.basicConfig(format='%(asctime)s - %(process)d - %(levelname)s - %(message)s', level=logging.DEBUG)

load_dotenv(find_dotenv())

def owm_req(location, units):
    w_url = "https://api.openweathermap.org/data/2.5/weather?"
    w_params = {"q": location, "units": units, "appid": os.getenv("OWM_KEY")}
    return requests.get(w_url, params=w_params)

def aqi_req(aq_token, lat, lon):
    aq_url = f"https://api.waqi.info/feed/geo:{str(lat)};{str(lon)}/?token={aq_token}"
    return requests.get(aq_url)


app = Flask(__name__)
@app.route("/")
def weather():
    location = request.args.get("location")
    units = request.args.get("units")

    if location is None:
        #ip_addr = request.headers.getlist("X-Real-Ip")
        ip_addr = request.headers.getlist("CF-Connecting-IP")
        if ip_addr[0] == "192.168.1.1":
            location = geocoder.ip('me').address
        else:
            location = geocoder.ip(ip_addr[0]).address
    if units is None:
        units = "imperial"

    owm = owm_req(location, units)
    print(owm.json())
    lat = owm.json()['coord']['lat']
    lon = owm.json()['coord']['lon']

    aq_req = aqi_req(os.getenv("WAQI_KEY"), lat, lon)

    loc_name = str(owm.json()['name'])
    current = str(owm.json()['main']['temp'])
    high = str(owm.json()['main']['temp_max'])
    low = str(owm.json()['main']['temp_min'])
    humidity = str(owm.json()['main']['humidity']) + "%"
    conditions = owm.json()['weather'][0]['description']
    aqi = aq_req.json()['data']['aqi']


    w_table = PrettyTable()
    w_table.field_names =["Location", loc_name]
    w_table.add_rows(
        [
            ["Current", current],
            ["High", high],
            ["Low", low],
            ["Humidity", humidity],
            ["Conditions", conditions],
            ["AQI", str(aqi)]
        ]
    )

    w_table.border = True

    if "curl" in request.headers.get('User-Agent'):
        result = w_table.get_string()
        return result
    else:
        result = w_table.get_html_string(format=True)
        return render_template('table.html', result=result)

@app.route("/dranks")
def beer_time():
    exclusions = ["+", "-", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
    places = []
    for tz in pytz.all_timezones:
        teezee = pytz.timezone(tz)
        time_int = int(datetime.now(teezee).strftime("%H%M"))
        if time_int > 1700 and time_int < 1800:
            if any(x in tz for x in exclusions):
                continue
            else:
                places.append(tz.replace("_", " ").rsplit("/", 1)[-1])

    result = "It's 5pm in " + places[randrange(len(places))] + "!"
    return render_template("generic.html", result=result)

@app.route("/bananas")
def bananas():
    return render_template("bananas.html")

@app.route("/result",methods = ["POST", "GET"])
def result():
    if request.method == "POST":
        try:
            q = request.form["quantity"]
            unit = request.form["unit"]
        except:
            print("Try again, but this time do it right.")

        if unit in c.scale:
            multiplier = c.scale[unit]
        else:
            print("Try again, but this time do it right.")

        total = float(q) * multiplier
        result = str(q) + " " + unit + " is equivalent to " + str(round(total, 3)) + " bananas!"

        return render_template("bananas_result.html",result = result)
    elif request.method == "GET":
        return redirect("https://wgetweather.com/bananas", code=302)
    else:
        result = "You definitely did something wrong, and should be ashamed of yourself for it."
        return render_template("generic.html", result=result)
