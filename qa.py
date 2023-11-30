from scrape import get_recipe_info
from process_instructions import process_instructions
import re
from fractions import Fraction

from lists import ingredients as presaved_ingredients
from separate import get_ingredients_from_one_item as get_ingred


def google_search_query(query,youtube = False):
    
    query = query.replace(' ', '+')
    if(youtube):
        search_url = f'https://www.youtube.com/results?search_query={query}'
    else:
        search_url = f'https://www.google.com/search?q={query}'
    return search_url

def parse_question(input_str,instr_ptr, last_input, instruction_full=None, ingredients=None):
    instruction = instruction_full['text']
    items = instruction_full['ingredients'] + instruction_full['tools']
    print(instruction_full['ingredients'])
    actions = instruction_full['action']
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
    #Specific questions about the recipe:
    ## 1. If "ingred" is mentioned in question and ("list", "show") and "step" also mentioned -> the output will show ingredients mentioned in step
    ## 2. If ("convert" and "temp") or ("what is it in" and "cels"\"far"\"C"\"F") mentioned in qestion -> the output will show converted temperature
    ## 3. If ("convert" and "size") or ("what is it in" and "inch"\"cm"\"cent") mentioned in qestion -> the output will show converted sizes
    ## 4. ToDo "How much of ..."
    ## 5. ToDo "When was used ..."
    # ; etc
    # list ingred step

    elif("ingred" in input_str and  # show ingredients used in this step
         ("list" in input_str or "show" in input_str) and 
         "step" in input_str):
        print("These are the ingredients used in this step")
        # print(ingredients, instruction) #debug
        ingred_names = [ingredients[t]['name'] for t in ingredients]
        extr_ingr = []
        for id, i in enumerate(ingred_names):
            ingred_present = False
            for w in i.split(' '):
                if w in instruction.lower(): ingred_present = True
                if ingred_present: break
            if ingred_present: extr_ingr.append(i)
        output='\n'.join(extr_ingr) \
            if len(extr_ingr) > 0 \
                else "No ingredients mentioned"
    elif("convert" in input_str and "temp" in input_str) \
        or ("what is it in" in input_str \
            and ("cels" in input_str or "far" in input_str \
                 or "c" in input_str.split() or "f" in input_str.split())):   # convertion questions for C <-> F
        f_temp_pattern = r'\b(\d+)\s*(?:degree[s]\s*)?[Ff]\b'
        c_temp_pattern = r'\b(\d+)\s*(?:degree[s]\s*)?[Cc]\b'

        match_f = re.findall(f_temp_pattern, instruction.lower())
        match_c = re.findall(c_temp_pattern, instruction.lower())
        units = ['F', 'C']
        new_units = ['C', 'F']
        converters = [(lambda x: (x - 32) * 5 / 9), (lambda x: x * 9 / 5 + 32)]
        output = ''

        for matches, unit, new_unit, converter in zip([match_f, match_c], units, new_units, converters):
            for m in matches:
                cur_temp = float(m)
                new_temp = converter(cur_temp)
                output += f'The mentioned temperature of {cur_temp} {unit} can be converted to {new_temp} {new_unit}\n'
        if len(output) < 1: output = f'No temperatre mentioned in the step'
    elif("convert" in input_str and "size" in input_str) \
        or ("what is it in" in input_str \
            and ("inch" in input_str or "cm" in input_str or "cent" in input_str)):   # convertion questions for inch <-> cm
        pat_numbers = re.findall(r'\d+(?:\.\d+)?(?:/\d+)?', instruction.lower())
        numbers = []
        for number in pat_numbers:
            if '/' in number: numbers.append(float(Fraction(number)))
            elif '.' in number: numbers.append(float(number))
            else: numbers.append(float(number))
        unit = ''
        new_unit = ''
        conv = 0
        output = ''
        if 'cm' in instruction.lower().split():
            conv = 0.3937
            unit = 'cm'
            new_unit = 'in'
        if "inch" in instruction.lower().split():
            conv = 2.54
            unit = 'in'
            new_unit = 'cm'
        if conv == 0:
            output = "No mentions of size in the step"
        else:
            for number in numbers:
                output += f'The mentioned size of  {number} {unit} can be converted to {number * conv} {new_unit}\n'



    #vague questions
    elif("what is that" in input_str):
        print("I'm not entirely sure what you mean, but I'll try my best.")
        found = False
        if(items != None):
            for item in items:
                ans = input(f'Are you asking about the {item}?')
                if('y' in ans.lower()):
                    print('Here is a link that might help!')
                    output = google_search_query(f'what is {item}')
                    found = True
                else:
                    continue
            if not found:
                output = 'I can not figure out what you mean, please be more specific'
    elif("how" in input_str and "do that" in input_str):
        print("I'm not entirely sure what you mean, but I'll try my best.")
        found = False
        if(actions != None):
            for action in actions:
                ans = input(f'Are you asking about how to {action}?')
                if('y' in ans.lower()):
                    print('Here is a link that might help!')
                    output = google_search_query(f'how do I {action} for cooking', True)
                    found = True
                else:
                    continue
            if not found:
                output = 'I can not figure out what you mean, please be more specific'



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
    # url = 'https://www.foodnetwork.com/recipes/banana-bread-recipe-1969572' #DEBUG
    recipe = get_recipe_info(url)
    title = recipe['title']
    ingredients = recipe['ingredients']
    separated_ingredients = {} # it will have structure: {ingredients[i]: {"name": extracted_name, "info": {"amount":..., "measure":..., "prep":...}, "used_in_step":...}
    for element in ingredients:
        ingred_info, name = get_ingred(element)
        separated_ingredients[element] = {"name": name, "info": ingred_info, "used_in_step":0}
    # exact_ingredient = [exact_ingredient_extraction(el) for el in ingredients]
    instructions = recipe['instructions']
    # info = get_recipe_info(url)
    instructions = process_instructions(instructions,recipe)
    print(f'Let\' get started on {title}. How would you like to start?')
    while(True):
        choice = input('[1] Recipes or [2] Ingredients: ')
        if('ingred' not in choice):
            print("Let\' get started with the recipe. When you are ready to go to the next step please input the word 'continue'")
            break
        else:
            for element in ingredients:
                print(f'✦  {element}')
            print("Let\' get started with the recipe. When you are ready to go to the next step please input the word 'continue'")
            # print(ingredients)
            break
    instr_ptr = 0
    last_instr = None
    while(True):
        print(f'{instr_ptr+1}: {instructions[instr_ptr]["text"]}')
        input_str = input(":")
        instr_ptr, last_instr, output = parse_question(input_str, instr_ptr, last_instr, 
                                                       instructions[instr_ptr], 
                                                       separated_ingredients)
        print(f'{output}')
    
    
if __name__ == "__main__":
    session()

