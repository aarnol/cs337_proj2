from scrape import get_recipe_info
from process_instructions import process_instructions
def parse_question(input_str,last_instr,instr_ptr):
    new_ptr = instr_ptr
    if("repeat" in input_str):
        pass
    elif("next" in input_str or "continue" in input_str):
        new_ptr = instr_ptr + 1
    return new_ptr
    

def session():
    url = input("Please type the URL of the recipe: ")
    recipe = get_recipe_info(url)
    title = recipe['title']
    ingredients = recipe['ingredients']
    instructions =recipe['instructions']
    info = get_recipe_info(url)
    instructions = process_instructions(instructions,recipe)
    print(f'Let\' get started on {title}. How would you like to start?')
    while(True):
        choice = input('[1] Instuctions or [2] Recipes: ')
        if(choice is '1'):
            print("Let\' get started with the recipe.")
            break
        elif(choice is '2'):
            print(ingredients)
        else:
            'Please input 1 or 2'
    instr_ptr = 0
    while(True):
        print()
    
    

