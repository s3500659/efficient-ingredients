import requests

base_url = "https://api.spoonacular.com/recipes/"
api_key = "0c6d5f1efcdd4e9f969f719272f2161d"


def get_ingredients_visualized(id):
    default_css = True
    url = f'https://api.spoonacular.com/recipes/{id}/ingredientWidget?apiKey={api_key}&defaultCss={default_css}'

    response = requests.get(url)
    data = response.text

    return data


def get_recipe_information(id):
    """
    Use a recipe id to get full information about a recipe, 
    such as ingredients, nutrition, diet and allergen information, etc.
    """
    include_nutrition = True
    url = f'https://api.spoonacular.com/recipes/{id}/information?apiKey={api_key}&includeNutrition={include_nutrition}'
    response = requests.get(url)
    data = response.json()

    return data


def get_recipe_instructions(id):
    url = f'https://api.spoonacular.com/recipes/analyzeInstructions?apiKey={api_key}'

    response = requests.post(url, id)
    instruction = response.json()

    return instruction


def get_recipe_short_description(id):
    """Get a short description of the recipe using -- id.
    -- id: the id of the recipe
    """

    url = f"https://api.spoonacular.com/recipes/{id}/summary?apiKey={api_key}"
    response = requests.get(url)
    desc = response.json()
    return desc


def find_recipes_by_ingredients(ingredients):
    """
    Get recipes that include ingredients from -- ingredients
    -- ingredients: a comma separated string of ingredients
    -- returns: the recipes in json format.
    """

    url = f'https://p9wdrzcnii.execute-api.us-east-1.amazonaws.com/prod/getRecipeByIngredients?ingredients={ingredients}'
    response = requests.get(url)
    recipes = response.json()
    return recipes
