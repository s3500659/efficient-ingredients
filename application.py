import json
from flask import Flask, render_template, request, redirect, session, flash, url_for
from infrastructure.db_pantry import *
from infrastructure import s3_manager
import spoonacular


application = Flask(__name__)
application.secret_key = 'my secret key'

pantry_tableName = "pantry"
s3_recipe_bucket = 's3500659-recipes'

pantry_db = DbPantry(pantry_tableName)

user = 'vinh'

@application.route("/<id>/unsave_recipe")
def unsave_recipe(id):
    # remove recipe from saved
    s3_manager.delete_recipe(s3_recipe_bucket,id)

    return redirect(url_for("get_recipe_details", id=id))

@application.route("/<id>/save_recipe")
def save_recipe(id):
    # save recipe to s3 for analytics purposes
    recipe = spoonacular.get_recipe_information(id)
    s3_manager.upload_recipe(recipe, s3_recipe_bucket, str(id))

    return redirect(url_for("get_recipe_details", id=id))


@application.route("/<id>/get_recipe_details")
def get_recipe_details(id):
    """
    Get the selected recipe details
    """
    # get the recipe
    recipe_exist = bool(s3_manager.check_recipe_exist(s3_recipe_bucket, id))
    recipe = None
    if recipe_exist == False:
        recipe = spoonacular.get_recipe_information(id)
    else:
        recipe = s3_manager.download_recipe(s3_recipe_bucket, id)

    return render_template('recipe_details.html', recipe=recipe, exist=recipe_exist)


@application.route("/search_by_recipe_name")
def search_by_recipe_name():
    """
    Search the Spoonacular api for a recipe by name.
    """

    return "Under construction"


@application.route("/search_by_ingredients")
def search_by_ingredients():
    """
    Search the Spoonacular api for recipes that includes the ingredients from the user's pantry.
    """
    # get the ingredients from db
    ingredients = pantry_db.get_items(user=user)

    ingredients_list = []
    for item in ingredients:
        ingredients_list.append(item['ingredient'])
    query_string = ",".join(ingredients_list)
    response = spoonacular.find_recipes_by_ingredients(query_string)
    recipes = response['recipes']

    return render_template('recipes.html', recipes=recipes)


@application.route("/<ingredient>/remove_ingredient")
def remove_ingredient(ingredient):

    return "todo add ingredients"


@application.route("/add_ingredient", methods=['POST'])
def add_ingredient():
    ingredient = request.form['ingredient']
    expiry = request.form['expiry_date']

    pantry_db.add_item(user, ingredient, expiry)
    return redirect(url_for("pantry"))


@application.route("/pantry")
def pantry():

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
    # create recipe s3 bucket
    s3_manager.create_bucket(s3_recipe_bucket)

    application.run(host="0.0.0.0", port=8080, debug=True)
