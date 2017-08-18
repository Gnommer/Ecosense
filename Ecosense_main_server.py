from flask import Flask, flash, redirect, render_template, request, session, abort, jsonify
import sqlite3 as sql
import os
import requests
import json
import pandas as pd
from flask_cors import CORS, cross_origin
from sklearn.neural_network import MLPRegressor
import numpy as np
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler


class data_analysis:
	clf=0
	preferred = 0
	predicted = 0
	inner = 0
	outer = 0
	humidity = 0
	status = 0
	def gen_model(self):
                with sql.connect("ECOSENSE.db") as conn:
                        curs = conn.cursor()
                        print("Generating model....")
                        data=  pd.read_sql_query("SELECT inner,outer,humidity,prefered FROM Readings;", conn)
                        train_x=data[["inner","humidity","outer"]].values;
                        train_y=data["prefered"].values;
                        classif= MLPRegressor(solver='sgd',activation='logistic',hidden_layer_sizes=(25,20,15,10,5,4,3,2));
                        data_analysis.clf = classif.fit(train_x, train_y)
                        print("Model Created.!\n")
                        		
	def pred_temp(self, test):
                return round(data_analysis.clf.predict(test)[0],0)

	def train_model(self, pref_temp, test):
            	data_analysis.clf.partial_fit(test,[pref_temp])
		
def generate_model():
	analyse_object.gen_model()

def predict_temp(test):
	return analyse_object.pred_temp(test)
	
def anomaly(pref,test):
        analyse_object.train_model(pref,test)


analyse_object=data_analysis()
analyse_object.gen_model()


def insert_db_for_retrain():
        if(analyse_object.predicted == 0 and analyse_object.inner == 0 and analyse_object.humidity == 0 and analyse_object.outer == 0):
                return "OK"
        
        else:
                with sql.connect("ECOSENSE.db") as conn:
                        curs = conn.cursor()
                        curs.execute('''insert into Readings values(DateTime('now','localtime'),? ,? ,? ,?);''',(analyse_object.predicted,analyse_object.inner,analyse_object.humidity, analyse_object.outer))
                        print("Inserted")
                if(analyse_object.status == 1):
                        anomaly(analyse_object.preferred,[[analyse_object.inner,analyse_object.humidity, analyse_object.outer]])
                        analyse_object.status = 0;
                        
                        


scheduler = BackgroundScheduler()
scheduler.start()

scheduler.add_job(insert_db_for_retrain,'interval',minutes = 2,id='inserting into db',name='insert into db every 1 hour',start_date = '2017-01-01 00:00:00',replace_existing=True)
scheduler.add_job(analyse_object.gen_model,'interval',hours = 24,id='generate_model',name='generating model every 24 hours',start_date = '2017-01-01 00:00:00',replace_existing=True)

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

app = Flask(__name__)
CORS(app)
print('Server started')

@app.route('/login', methods=['GET','POST'])
def login_page():
	if request.form['password'] == 'admin' and request.form['username']=='admin':
		session['logged_in'] = True
	else:
		flash('Please check the username and password and try again')
	return home()

@app.route("/logout")
def logout():
    session['logged_in'] = False
    flash('Successfully logged out. Please log in again to access dashboard.')
    return home()

@app.route('/')
@cross_origin()
def home():
	if not session.get('logged_in'):
		return render_template('login.html')
	else:
		return render_template('t_index.html')	
	  

@app.route('/dialchanged', methods=['POST'])
def configuration_for_pi():
	user_prefered_temp = request.form['temp_setting']
	print("User Response: ", user_prefered_temp)
	analyse_object.status = 1;
	analyse_object.predicted = user_prefered_temp	
	jdata ={
		'user_setting': analyse_object.predicted
	       }
	
	requests.post('PI_IP_ADDRESS/setslavesetting', json = jdata)
	return jsonify(jdata)

@app.route('/prediction', methods=['GET','POST'])
def hourly_prediction():
	uresponse = request.get_json()
	data =json.loads(uresponse)
	test =[[data["inner"], data["humidity"], data["outer"]]]
	predicted_setting = predict_temp(test)
	analyse_object.inner = data["inner"]
	analyse_object.humidity = data["humidity"]
	analyse_object.outer = data["outer"]
	analyse_object.preferred = data["setting"]
	analyse_object.predicted = predicted_setting
	jdata ={
		'user_setting': analyse_object.predicted
	       }
	return json.dumps({"result": predicted_setting})

       
@app.route('/morrisdata', methods=['GET'])
def morissis():
        with sql.connect("ECOSENSE.db") as conn:
                curs = conn.cursor()
                df = pd.read_sql_query(
				"SELECT date,inner,outer,humidity FROM Readings LIMIT 10 OFFSET(SELECT COUNT(*) FROM Readings) - 10;"
				, conn)
                jsondata1 = df.to_json(orient = 'records')
                df2 = pd.read_sql_query(
				"SELECT date,inner,prefered FROM Readings LIMIT 10 OFFSET(SELECT COUNT(*) FROM Readings) - 10;"
				, conn)
                jsondata2 = df2.to_json(orient = 'records')
                jsonpacked = {
                                'graph1':json.loads(jsondata1),
                                'graph2':json.loads(jsondata2)
                             }
        return jsonify(jsonpacked)

@app.route('/getsetting', methods=['POST','GET'])
def pi_temp_get():
        uresponse = requests.get("PI_IP_ADDRESS/getslavesetting")
        data =uresponse.json()
        analyse_object.inner = data["inner"]
        analyse_object.humidity = data["humidity"]
        analyse_object.outer = data["outer"]
        analyse_object.preferred = data["setting"]
        return jsonify(uresponse.json())



if __name__=='__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True, port=9000, host='0.0.0.0',use_reloader=False)
