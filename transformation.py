from qa import google_search_query
import re
from scrape import get_recipe_info
from process_instructions import process_instructions

meat_subs = {
    "chicken": {"substitute": "tofu", "proportion": None},
    "beef": {"substitute": "black beans", "proportion": ('cup', 'pound')},
    "pork": {"substitute": "lentils", "proportion": ('cup', 'pound')},
    "fish": {"substitute": "tofu", "proportion": None},
    "shrimp": {"substitute": "tofu", "proportion": None},
    "bacon": {"substitute": "tempeh", "proportion": None},
    "sausage": {"substitute": "soy sausage", "proportion": None},
    "turkey": {"substitute": "tofu", "proportion": None},
    "ham": {"substitute": "jackfruit", "proportion": None},
    "lamb": {"substitute": "lentils ", "proportion": ('cup', 'pound')},
    "veal": {"substitute": "eggplant", "proportion": ('cup', 'pound')},
    "venison": {"substitute": "mushrooms", "proportion": ('cup', 'pound')},
    "duck": {"substitute": "seitan", "proportion": ('cup', 'pound')},
    "rabbit": {"substitute": "tofu", "proportion": None},
    "salmon": {"substitute": "tofu", "proportion": None},
    "crab": {"substitute": "jackfruit", "proportion": None},
    "lobster": {"substitute": "heart of palm", "proportion": None},
    "clams": {"substitute": "oyster mushrooms", "proportion": None},
    "anchovies": {"substitute": "nori seaweed strips", "proportion": None},
}

def veggify(proccessed_instructions, ingredients):
    for key in meat_subs.keys():
        for i in range(len(proccessed_instructions)):
            proccessed_instructions[i]['ingredients'] = [re.sub(key,meat_subs[key]['substitute'], ingred) \
                                                            for ingred in proccessed_instructions[i]['ingredients']]
            proccessed_instructions[i]['text'] = re.sub(key, meat_subs[key]['substitute'],proccessed_instructions[i]['text'])
        ingredients = [re.sub(f"{key} (.*)",meat_subs[key]['substitute'], x) for x in ingredients] # need to change once we parse ingredients?
    return proccessed_instructions, ingredients

    
if __name__ == "__main__":
    url = 'https://www.foodnetwork.com/recipes/food-network-kitchen/the-best-chicken-noodle-soup-7194859' #DEBUG
    recipe = get_recipe_info(url)
    instructions  = recipe['instructions']
    ingredients = recipe['ingredients']
    print(ingredients)
    processed = process_instructions(instructions,recipe)
    print(processed)
    new_instr, new_dict = veggify(processed,ingredients)
    print("NEW")
    print(new_instr)
    print(new_dict)
