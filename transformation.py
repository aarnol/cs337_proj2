from utils import google_search_query
import re
from scrape import get_recipe_info
from process_instructions import process_instructions
from fractions import Fraction


def transform(proccessed_instructions, separated_ingredients, transform):
    new_sep_ingreds = {}
    for key in transform.keys():
        for i in range(len(proccessed_instructions)):
            proccessed_instructions[i]['ingredients'] = [re.sub(key,transform[key]['substitute'], ingred) \
                                                            for ingred in proccessed_instructions[i]['ingredients']]
            proccessed_instructions[i]['text'] = re.sub(key, transform[key]['substitute'],proccessed_instructions[i]['text'])
        # ingredients = [re.sub(f"{key} (.*)",transform[key]['substitute'], x) for x in ingredients] 
    for old_ingred in separated_ingredients.keys():
        old_name = separated_ingredients[old_ingred]['name']
        key = old_ingred
        name = separated_ingredients[old_ingred]['name']
        info = separated_ingredients[old_ingred]['info']
        amount = info['amount']
        measure = info['measure']
        for sub in transform:
            
            if sub in name or sub in key:
                name = transform[sub]['substitute']
                
                key = transform[sub]['substitute']
                if(transform[sub]['proportion']!= None):
                    if transform[sub]['proportion'][1] in info['measure']:
                        measure = transform[sub]['proportion'][0] + 's'
                if(transform[sub]['amount'] != None):
                    try:
                        amount = int(amount) *transform[sub]['amount']
                        
                    except:
                        amount = Fraction(amount) * transform[sub]['amount']
                        
                        
                        
                info = {'amount':amount, 'measure': measure, 'prep':info['prep']}
                print(info)
                print(name)
                print(key)
        new_sep_ingreds[key] = {'name':name, 'info':info}

    return proccessed_instructions, new_sep_ingreds

    

