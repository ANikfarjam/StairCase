#author: Ashkan Nikfarjam

from flask import Flask, jsonify
from flask_cors import CORS
from BackEnd.Routers.StartingGameRout import start_BP
from BackEnd.Routers.menue_rout import menue_bp
from BackEnd.app import app
#initiate app and define cores

# app = Flask(__name__)
# allow universal requests
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

"""
register routs:
app.register_blueprint(rout)
"""
#register start game API
app.register_blueprint(start_BP)
app.register_blueprint(menue_bp)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

