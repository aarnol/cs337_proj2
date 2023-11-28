from scrape import get_recipe_info
from process_instructions import process_instructions
import re
def google_search_query(query,youtube = False):
    
    query = query.replace(' ', '+')
    if(youtube):
        search_url = f'https://www.youtube.com/results?search_query={query}'
    else:
        search_url = f'https://www.google.com/search?q={query}'
    return search_url

def parse_question(input_str,instr_ptr, last_input):
    output = None
    skip_pattern = r'\bgo to step (\d+)\b'
    input_str = input_str.lower()
    new_ptr = instr_ptr
    #navigation
    if("repeat" in input_str):
        pass
    elif("next" in input_str or "continue" in input_str):
        new_ptr = instr_ptr + 1
    elif(re.search(skip_pattern, input_str)):
        match = re.search(skip_pattern, input_str).group(1)
        new_ptr = int(match) - 1
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
        if(choice == '1'):
            print("Let\' get started with the recipe.")
            break
        elif(choice == '2'):
            print(ingredients)
        else:
            'Please input 1 or 2'
    instr_ptr = 0
    last_instr = None
    while(True):
        print(f'{instr_ptr+1}: {instructions[instr_ptr]['text']}')
        input_str = input(":")
        instr_ptr, last_instr, output = parse_question(input_str, instr_ptr, last_instr)

    
    
if __name__ == "__main__":
    session()

