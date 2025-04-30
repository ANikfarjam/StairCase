#author: Ashkan Nikfarjam

from flask import Flask, jsonify
from flask_cors import CORS
from BackEnd.Routers.StartingGameRout import start_BP
#initiate app and define cores

app = Flask(__name__)
# allow universal requests
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

"""
register routs:
app.register_blueprint(rout)
"""
#register start game API
app.register_blueprint(start_BP)
if __name__ == '__main__':
    app.run(debug=True)