from flask import Flask, request, jsonify, render_template
from flask.views import F
from pymongo import MongoClient
from sqlalchemy import Result
from config import MONGO_URI
from Retriver_model import model

app = Flask(__name__)

client = MongoClient(MONGO_URI)
db = client["flaskdb"]
users_collection = db["users"]

@app.route("/",methods=["GET", "POST"])
def home():
    show_textarea = False
    answer = ""
    if request.method == "POST":
        if "Submit" in request.form:
            show_textarea=True
        if "get_answer" in request.form:
            show_textarea=True
            answer=get_answer()
        
    return render_template("mainpage.html",show_textarea=show_textarea,answer=answer)

def get_answer():
    if request.method=="POST":
         Question= request.form.get("question")
         answer="I Love you"
    return answer

if __name__ == "__main__":
    app.run(debug=True)