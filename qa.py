from scrape import get_recipe_info
from process_instructions import process_instructions
import re
from lists import ingredients as presaved_ingredients


def google_search_query(query,youtube = False):
    
    query = query.replace(' ', '+')
    if(youtube):
        search_url = f'https://www.youtube.com/results?search_query={query}'
    else:
        search_url = f'https://www.google.com/search?q={query}'
    return search_url

def parse_question(input_str,instr_ptr, last_input, instruction=None):
    output = None
    skip_pattern = r'\bgo to step (\d+)\b'
    skip_pattern = r'\bto step (\d+)\b' # so that it would also take patter "take me to" not only "go to"
    input_str = input_str.lower()
    new_ptr = instr_ptr
    #navigation
    if("repeat" in input_str):
        pass
    elif("next" in input_str or "continue" in input_str):
        new_ptr = instr_ptr + 1
    elif("back" in input_str or "previous" in input_str):
        new_ptr = instr_ptr - 1
    elif(re.search(skip_pattern, input_str)):
        match = re.search(skip_pattern, input_str).group(1)
        new_ptr = int(match) - 1
    #Specific questions about the recipe
    # ingredients in this step
    # what is it in F to C; inch to cm; etc
    # what temperature

    elif("ingredient in the" in input_str and instruction):
        print("These are the ingredients used in this step")
        extr_ingr = exact_ingredient_extraction(instruction)
        output= '\n'.join(extr_ingr) if len(extr_ingr) > 0 else "No ingredients mentioned"
    #vague questions
    elif("what is that" in input_str):
        pass
    elif("what is" in input_str):
        print("I'm not sure, but here is a google link that might help.")
        output = google_search_query(input_str)
    elif("how do" in input_str):
        print("I'm not sure, but here is a google link that might help.")
        output = google_search_query(input_str,youtube=True)
    return new_ptr, input_str, output
    

def exact_ingredient_extraction(ingredients_el):
    return [t.replace('_', ' ') for t in presaved_ingredients if t.replace('_', ' ') in ingredients_el]

def session():
    url = input("Please type the URL of the recipe: ")
    recipe = get_recipe_info(url)
    title = recipe['title']
    ingredients = recipe['ingredients']
    # exact_ingredient = [exact_ingredient_extraction(el) for el in ingredients]
    instructions = recipe['instructions']
    info = get_recipe_info(url)
    instructions = process_instructions(instructions,recipe)
    print(f'Let\' get started on {title}. How would you like to start?')
    while(True):
        choice = input('[1] Recipes or [2] Ingredients: ')
        if(choice == '1'):
            print("Let\' get started with the recipe. When you are ready to go to the next step please input the word 'continue'")
            break
        elif(choice == '2'):
            for element in ingredients:
                print(f'✦  {element}')
            print("Let\' get started with the recipe. When you are ready to go to the next step please input the word 'continue'")
            # print(ingredients)
            break
        else:
            'Please input 1 or 2'
    instr_ptr = 0
    last_instr = None
    while(True):
        print(f'{instr_ptr+1}: {instructions[instr_ptr]["text"]}')
        input_str = input(":")
        instr_ptr, last_instr, output = parse_question(input_str, instr_ptr, last_instr, instructions[instr_ptr])
        print(f'{output}')
    
    
if __name__ == "__main__":
    session()

