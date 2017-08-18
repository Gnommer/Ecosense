from flask import Flask, flash, redirect, render_template, request, session, abort, jsonify
import os
import json
from flask_cors import CORS, cross_origin
class ecoslave:
        roomstate_ac_setting = 0
        roomstate_inner_temperature = 0
        roomstate_inner_humidity = 0
        roomstate_outer_temperature = 0
        
        def roomstate_set_inner(self):
                self.roomstate_inner_temperature = 20
                self.roomstate_inner_humidity = 40
                
        def roomstate_set_outer(self):
                self.roomstate_outer_temperature = 30

        def roomstate_set_ac(self,temp):
                self.roomstate_ac_setting = temp

        def roomstate_get(self):
                roomstate = {
                             "inner": self.roomstate_inner_temperature,
                             "humidity": self.roomstate_inner_humidity,
                             "outer": self.roomstate_outer_temperature,
                             "setting": self.roomstate_ac_setting
                            }
                return roomstate
#saving state
       
pislave = ecoslave()
pislave.roomstate_set_inner()
pislave.roomstate_set_ac(20)
pislave.roomstate_set_outer()

app = Flask(__name__)
CORS(app)

print('Server started')		

@app.route('/setslavesetting', methods=['POST'])
def pi_setting_set():
	pislave.roomstate_set_ac(request.json["user_setting"])
	print(pitemp.countget())
	return "set"

@app.route('/getslavesetting', methods=['GET'])
def pi_setting_get():
        room = pislave.roomstate_get()
        return jsonify(room)  

if __name__=='__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True, port=9002, host='0.0.0.0')
