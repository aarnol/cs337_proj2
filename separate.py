import re
import os

import nltk
from nltk import pos_tag, word_tokenize

from scrape import get_recipe_info

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

measure_pattern = re.compile(r'(cups?|teaspoons?|tablespoons?|cloves?|pounds?|ounces?)')

# extracts a patter of numbers (could be a fraction) divided by a word to (or just separated)    
def extract_amount(text): 
    amounts_elements = '0123456789 /to'
    all_matches, cur_match = [], []
    non_amount_info = ''
    for id, el in enumerate(text):
        if el in amounts_elements \
            and ((el != ' ') or (len(cur_match) > 0)) \
            and ((el != 'o') or (len(cur_match) > 1 and cur_match[-1] == 't')) \
            and ((el != 't') or (len(cur_match) > 0 and id < len(text) - 1 and text[id+1] == 'o')): 
            cur_match.append(el)
        else:
            non_amount_info += el
            if len(cur_match) > 0: all_matches.append((''.join(cur_match)).strip())
            cur_match = []
    if len(cur_match) > 0: all_matches.append(''.join(cur_match))
    return all_matches, non_amount_info.strip()

def get_ingredients(recipe_info):
    # ingredients: {'amount':    ,'measure':   , 'prep':   }
    ingredients_dict = {}
    for item in recipe_info['ingredients']:
        # Get instructions in brackets
        additional_measure = None
        match = re.search(r'\((.*?)\)', item)
        if match:
            additional_measure = match.group(1)
        # Remove brackets content
        item = re.sub(r'\([^)]*\)', '', item)
        # Remove punctuation
        ingredient_name_str = item.split(',')[0]
        item = re.sub(r'[^\w\s/.,]', ' ', item)
        # Get verbs
        words = word_tokenize(item)
        pos_tags = pos_tag(words)
        actions = [word for word, pos in pos_tags if pos.startswith('VB')]
        # Get amounts and measure types
        amounts, _ = extract_amount(item)
        _, ingredient_name_str = extract_amount(ingredient_name_str) # remove amounts
        measures = measure_pattern.search(item)
        if measures: measures = measures.group()
        else: measures = []
        # Remove particles
        ingredient_name_str = re.sub(r'and ', '', ingredient_name_str)
        # Remove the measures and actions from the string 
        ingredient_list = []
        for word in ingredient_name_str.split():
            if word in measures or word == measures or word in actions: continue
            ingredient_list.append(word)
        ingredient_name = ' '.join(ingredient_list)
        
        amount = amounts[0] if len(amounts) > 0 else None
        measure = measures if len(measures) > 0 else None
        ingredients_dict[ingredient_name] = {'amount': amount,
                                             'measure': measure,
                                             'prep': actions}
        # print('Initial:', item, '\n', 'Ingredienet name:', ingredient_name, '   ->   ',
        #       ingredients_dict[ingredient_name], '\n', '--' * 8)
    return ingredients_dict

if __name__ == '__main__':
    
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
        
        print("Parsed ingredients")
        ingredients_dict = get_ingredients(recipe_info)
        # print(ingredients_dict)

        
