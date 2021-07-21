from flask import Flask, render_template, request, redirect, session, flash, url_for
from models.db_pantry import *

application = Flask(__name__)
application.secret_key = 'my secret key'

pantry_tableName = "pantry"
pantry_db = DbPantry(pantry_tableName)



@application.route("/<ingredient>/remove_ingredient")
def remove_ingredient(ingredient):
    
    return "todo add ingredients"

@application.route("/add_ingredient", methods=['POST'])
def add_ingredient():
    user = 'vinh'
    ingredient = request.form['ingredient']

    pantry_db.add_item(user, ingredient)
    return redirect(url_for("pantry"))

@application.route("/pantry")
def pantry():
    user = 'vinh'
    # get all ingredients for current user
    ingredients = pantry_db.get_items(user)
    return render_template('pantry.html', ingredients=ingredients)

@application.route("/login")
def login():

    return redirect(url_for("pantry"))

@application.route("/")
def main():
    return redirect(url_for("pantry"))


if __name__ == "__main__":
    # create pantry table in DynamoDb
    pantry_db.create_pantry()



    application.run(host="0.0.0.0", port=8080, debug=True)