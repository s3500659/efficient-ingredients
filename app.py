import json
from flask import Flask, render_template, request, redirect, session, flash, url_for
from infrastructure.db_pantry import *
from infrastructure import s3_manager, db_user, db_manager, kinesis_ds
from boto3.dynamodb.conditions import Key, Attr
import spoonacular
import pprint


app = Flask(__name__)
app.secret_key = 'my secret key'

table_pantry = "pantry"
table_saved_recipe = "saved_recipe"
s3_recipe_bucket = 's3500659-recipes'
ds_trending_recipes = 'ef-trending-recipes'

pantry_db = DbPantry(table_pantry)


@app.route('/saved_recipes')
def saved_recipes():
    """ Get the user saved recipes from database then present them to the user """
    # get user saved recipes from database
    table = db_manager.get_table(table_saved_recipe)
    response = table.query(
        KeyConditionExpression=Key('user').eq(session['email'])
    )
    items = response['Items']
    # get all recipes from s3
    recipes = []
    for item in items:
        recipe = s3_manager.download_recipe(
            s3_recipe_bucket, item['recipe_id'])
        recipes.append(recipe)

    return render_template('saved_recipes.html', recipes=recipes)


@app.route("/<id>/unsave_recipe")
def unsave_recipe(id):
    # remove recipe from saved
    s3_manager.delete_recipe(s3_recipe_bucket, id)

    return redirect(url_for("get_recipe_details", id=id))


@app.route("/<id>/save_recipe")
def save_recipe(id):
    # save recipe to s3 for analytics purposes
    recipe = spoonacular.get_recipe_information(id)
    s3_manager.upload_recipe(recipe, s3_recipe_bucket, str(id))
    # save user - recipe id to database
    table = db_manager.get_table(table_saved_recipe)
    table.put_item(
        Item={
            'user': session['email'],
            'recipe_id': str(id),
        }
    )

    return redirect(url_for("get_recipe_details", id=id))


@app.route("/<id>/get_recipe_details")
def get_recipe_details(id):
    """
    Get the selected recipe details
    """
    # get the recipe from api
    recipe_exist = bool(s3_manager.check_recipe_exist(s3_recipe_bucket, id))
    recipe = None
    if recipe_exist == False:
        response = spoonacular.get_recipe_information(id)
        recipe = response['recipe']
    else:
        # download saved recipe from s3
        # (this recipe was saved by the user and so we uploaded the recipe to s3 to save on api call)
        response = s3_manager.download_recipe(s3_recipe_bucket, id)
        recipe = response['recipe']

    # put recipe details to kinesis datastream
    ds = {'id': id}
    kinesis_ds.put_record(ds_trending_recipes, ds, 'recipe')

    return render_template('recipe_details.html', recipe=recipe, exist=recipe_exist)


@app.route("/search_by_recipe_name", methods=["POST"])
def search_by_recipe_name():
    """
    Search the Spoonacular api for a recipe by name.
    """
    recipe_name = request.form['recipe_name']
    recipes = spoonacular.get_recipes(recipe_name)
    recipes = recipes['results']

    return render_template('recipes.html', recipes=recipes, by_name=True)


@app.route("/search_by_ingredients")
def search_by_ingredients():
    """
    Search the Spoonacular api for recipes that includes the ingredients from the user's pantry.
    """
    # get the ingredients from db
    ingredients = pantry_db.get_items(session['email'])

    ingredients_list = []
    for item in ingredients:
        ingredients_list.append(item['ingredient'])
    query_string = ",".join(ingredients_list)
    response = spoonacular.find_recipes_by_ingredients(query_string)
    recipes = response['recipes']

    return render_template('recipes.html', recipes=recipes, by_name=False)


@app.route("/<ingredient>/remove_ingredient")
def remove_ingredient(ingredient):
    pantry_db.delete_item(session['email'], ingredient)
    return redirect(url_for('pantry'))


@app.route("/add_ingredient", methods=['POST'])
def add_ingredient():
    ingredient = request.form['ingredient']
    expiry = request.form['expiry_date']

    pantry_db.add_item(session['email'], ingredient, expiry)
    return redirect(url_for("pantry"))


@app.route("/pantry")
def pantry():
    # get trending recipes from s3
    trending_recipes_id = s3_manager.get_trending_recipe_id()
    trending_recipes = []
    for id in trending_recipes_id:
        trending_recipes.append(spoonacular.get_recipe_information(id))

    # get all ingredients for current user
    ingredients = pantry_db.get_items(session['email'])
    return render_template('pantry.html', ingredients=ingredients, trending_recipes=trending_recipes)


@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        pw = request.form['password']
        user_name = request.form['username']
        # check if user already exists
        user = db_user.get_user(email)
        if user == None:
            db_user.create_user(email, pw, user_name)
            flash('account created')
            return redirect(url_for('login'))
        else:
            flash('email already registered')

    return render_template('register.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = db_user.get_user(email)

        if user == None:
            flash('Invalid email or password')
            return redirect(url_for('login'))
        if user['email'] == email and user['password'] == password:
            session['email'] = user['email']
            return redirect(url_for("pantry"))
        else:
            flash('Invalid email or password')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route("/")
def main():
    return redirect(url_for("login"))


if __name__ == "__main__":
    # set up user table and test user
    if not db_user.table_exist():
        db_user.create_user_table()
    db_user.create_user('vinh@gmail.com', '123', 'Vinh Tran')
    # create pantry table in DynamoDb
    pantry_db.create_pantry()
    # create user saved recipe table
    db_manager.create_table('saved_recipe', 'user', 'recipe_id')
    # create recipe s3 bucket
    s3_manager.create_bucket(s3_recipe_bucket)
    # create new kinesis data stream
    kinesis_ds.create_stream(ds_trending_recipes, 1)

    app.run(host="0.0.0.0")
