import re
import os

import nltk
from nltk import pos_tag, word_tokenize
import spacy
from scrape import get_recipe_info
from separate import get_ingredients

pos_tagger = spacy.load("en_core_web_sm")
nltk.download('punkt')
nltk.download('maxent_ne_chunker')
nltk.download('words')
def steps_to_sentences(steps):
    sentences = []
    for step in steps:
        step = step.split(".")
        sentences += step
    sentences =[s for s in sentences if re.search('[a-zA-Z]', s)]
    return sentences

def process_instructions(instructions_list, recipe_info):
    processed_instructions = []

    # Retrieve ingredients dictionary
    ingredients_dict = get_ingredients(recipe_info)

    #lowercase all the instructions
    instructions_list = [instruction.lower() for instruction in instructions_list]
    instructions_list = steps_to_sentences(instructions_list)

    for step, instruction in enumerate(instructions_list, start=1):
        # For each instruction, create a dictionary that will hold the action, ingredients, and tools
        current_instruction = {
            'instruction_step': step,
            'action': [],
            'ingredients': [],
            'tools': []
        }

        # Remove punctuation
        instruction = re.sub(r'[^\w\s/.,]', ' ', instruction)

        # Get verbs
        words = word_tokenize(instruction)
        pos_tags = pos_tag(words)
        actions = [word for word, pos in pos_tags if pos.startswith('VB')]
        current_instruction['action'] = actions

        # Check if the ingredient is in the ingredients dictionary, if it is, add it to the ingredients list.
        for ingredient in ingredients_dict:
            if ingredient in instruction:
                current_instruction['ingredients'].append(ingredient)

        processed_instructions.append(current_instruction)

    return processed_instructions


if __name__ == '__main__':
    # url = 'https://www.foodnetwork.com/recipes/banana-bread-recipe-1969572'
    url = "https://www.foodnetwork.com/recipes/food-network-kitchen/yogurt-marinated-grilled-chicken-shawarma-9961050"

    recipe_info = get_recipe_info(url)

    if recipe_info:
        instructions = process_instructions(recipe_info['instructions'], recipe_info)
        print(instructions)
