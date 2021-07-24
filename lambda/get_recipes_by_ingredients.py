import requests


def lamda_handler(event, context):
    # get ingredient list passed in from user
    ingredients = event['queryStringParameters']['ingredients']

    # get ingredients from spoonacular
    response = find_recipes_by_ingredients(ingredients)

    # return response to user
    return response

def find_recipes_by_ingredients(ingredients):
    base_url = "https://api.spoonacular.com/recipes/"
    api_key = "0c6d5f1efcdd4e9f969f719272f2161d"
    limit = 20
    ranking = 2
    ignore_pantry = True

    url = f"{base_url}findByIngredients?apiKey={api_key}&ingredients={ingredients}&number={limit}&limitLicense=true&ranking={ranking}&ignorePantry={ignore_pantry}"

    response = requests.get(url)
    recipes = response.json()
    return recipes