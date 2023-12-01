from qa import google_search_query
import re
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

def veggify(proccessed_instructions, ingredients_dict):
    new_ingredients = {}
    for ingredient in ingredients_dict.keys():
        for key in meat_subs.keys():
            if key in ingredient:
                if(meat_subs['key']['proportion'] == None):
                    measure =ingredients_dict[ingredient]['measure']
                elif meat_subs['key']['proportion'][1] in ingredients_dict[ingredient]['measure']:
                    measure = meat_subs['key']['proportion'] + "s"
                else:
                    print("Could not verify measurements, but I've provided a helpful link to make the substitution correct")
                    print(google_search_query(f'ratio between {key} and {ingredient}'))
                    measure = "unknown"
                amount= ingredients_dict[ingredient]['amount']
                prep = ingredients_dict[ingredient]['prep']
                new_ingredients[meat_subs[key]['substitute']] = {'amount' :amount , 'measure':measure, "prep":prep}
    for key in meat_subs.keys():
        for i in range(len(proccessed_instructions)):
            proccessed_instructions[i]['ingredients'] = [re.sub(meat_subs[key]['substitute'],key, ingred) \
                                                            for ingred in proccessed_instructions[i]['ingredients']]
            proccessed_instructions[i]['text'] = re.sub(meat_subs[key]['substitute'],key, proccessed_instructions[i]['text'])
    return proccessed_instructions, ingredients_dict
    
    

