import requests

from bs4 import BeautifulSoup
import re


def get_recipe_info(url):
    # Send an HTTP request to the URL and retrieve the content
    response = requests.get(url)

    if response.status_code != 200:
        print("Failed to retrieve the webpage.")
        return

    # Parse the webpage content with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find and extract the recipe title
    recipe_title = soup.find('span', class_='o-AssetTitle__a-HeadlineText').get_text()

    # Find and extract the list of ingredients
    ingredients = []
    ingredient_list = soup.find_all('p', class_='o-Ingredients__a-Ingredient')

    for item in ingredient_list:
        item = item.next.next.next.next['value']
    
        ingredients.append(item)
    
    pattern = r'[0-9]'

    ingredients = ingredients[1:]
    # Find and extract the cooking instructions
    instructions = []
    instruction_list = soup.find_all('li', class_='o-Method__m-Step')

    for step in instruction_list:
        step = step.next
      
        instructions.append(step)

    return {
        'title': recipe_title,
        'ingredients': ingredients,
        'instructions': instructions
    }

if __name__ == '__main__':
    # Replace the URL with the Food Network recipe URL you want to scrape
    # url = 'https://www.foodnetwork.com/recipes/banana-bread-recipe-1969572'
    url = "https://www.foodnetwork.com/recipes/food-network-kitchen/yogurt-marinated-grilled-chicken-shawarma-9961050"

    recipe_info = get_recipe_info(url)

    if recipe_info:
        print(f"Recipe Title: {recipe_info['title']}\n")
        print("Ingredients:")
        for ingredient in recipe_info['ingredients']:
            print(ingredient)
        print("\nInstructions:")
        for i, step in enumerate(recipe_info['instructions'], 1):
            print(f"{i}. {step}")


