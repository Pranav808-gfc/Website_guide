from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from config import MONGO_URI

app = Flask(__name__)

client = MongoClient(MONGO_URI)
db = client["flaskdb"]
users_collection = db["users"]

@app.route("/", methods=["GET", "POST"])
def home():
    show_textarea=False

    if request.method=="POST":
       show_textarea= True
    else:
        show_textarea= False
    url= request.form.get("URL")
    return render_template("mainpage.html",show_textarea=show_textarea,info=url)

if __name__ == "__main__":
    app.run(debug=True)