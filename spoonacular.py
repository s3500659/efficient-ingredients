import requests

api_key = "0c6d5f1efcdd4e9f969f719272f2161d"


def get_recipes(recipe_name):
    number = 20 # The number of expected results (between 1 and 100).

    url = f'https://api.spoonacular.com/recipes/complexSearch?apiKey={api_key}&query={recipe_name}&number={number}'
    response = requests.get(url)
    data = response.json()

    return data


def get_recipe_information(id):
    """
    Use a recipe id to get full information about a recipe, 
    such as ingredients, nutrition, diet and allergen information, etc.
    """
    include_nutrition = True
    url = f'https://ao0syjui0f.execute-api.us-east-1.amazonaws.com/prod/get_recipe_information?apiKey={api_key}&id={id}'
    response = requests.get(url)
    data = response.json()

    return data


def find_recipes_by_ingredients(ingredients):
    """
    Get recipes that include ingredients from -- ingredients
    -- ingredients: a comma separated string of ingredients
    -- returns: the recipes in json format.
    """

    url = f'https://ao0syjui0f.execute-api.us-east-1.amazonaws.com/prod/get_recipes_by_ingredients?apiKey={api_key}&ingredients={ingredients}'
    response = requests.get(url)
    recipes = response.json()
    return recipes
