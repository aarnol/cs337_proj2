from scrape import get_recipe_info
from process_instructions import process_instructions
import re
from fractions import Fraction
from utils import google_search_query
from lists import health_subs, meat_subs
from lists import ingredients as presaved_ingredients
from separate import get_ingredients_from_one_item as get_ingred
from transformation import transform




def parse_question(input_str,instr_ptr, last_input, instruction_full=None, ingredients=None):
    instruction = instruction_full['text']
    items = instruction_full['ingredients'] + instruction_full['tools']
    # print(instruction_full['ingredients'])
    actions = instruction_full['action']
    output = None
    skip_pattern = r'\bgo to step (\d+)\b'
    skip_pattern = r'\bto step (\d+)\b' # so that it would also take patter "take me to" not only "go to"
    input_str = input_str.lower()
    new_ptr = instr_ptr
    output = ''
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
    ## 2. If ("convert" and "temp") or ("what is it in" and "cels"\"far"\"C"\"F") mentioned in question -> the output will show converted temperature
    ## 3. If ("convert" and "size") or ("what is it in" and "inch"\"cm"\"cent") mentioned in question -> the output will show converted sizes
    ## 4. if "how much of" is mentioned -> the output will show all measures and amounts of ingredients that were mentioned in the question
    ## 5. if "When was used" is mentioned -> the output will show in which steps were used ingredients that were mentioned in the question
    # ; etc
    # list ingred step

    elif("ingred" in input_str and  # show ingredients used in this step
         ("list" in input_str or "show" in input_str) and 
         "step" in input_str):
        print("These are the ingredients used in this step:")
        # print(ingredients, instruction) #debug
        ingred_names = [ingredients[t]['name'] for t in ingredients]
        extr_ingr = []
        for id, i in enumerate(ingred_names):
            ingred_present = False
            for w in i.split(' '):
                if w in instruction.lower(): ingred_present = True
                if ingred_present: break
            if ingred_present: extr_ingr.append(f'✦  {i}')
        output='\n'.join(extr_ingr) \
            if len(extr_ingr) > 0 \
                else "No ingredients mentioned"
    elif("ingred" in input_str and 'list' in input_str):
        for key in ingredients.keys():
            if(ingredients[key]['info']['measure']):
                measure = ingredients[key]['info']['measure']
            else:
                measure = ''
            print(f'✧ {ingredients[key]["info"]["amount"]} {measure} {ingredients[key]["name"]}') #✧ - not used; ✦ - used
            
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
    elif("how much" in input_str):
        ingred_names = [ingredients[t]['name'] for t in ingredients]
        ingred_amounts = {ingredients[t]['name']:ingredients[t]['info'] for t in ingredients}
        extr_ingr = []
        for id, i in enumerate(ingred_names):
            ingred_present = False
            for w in i.split(' '):
                if w in input_str: ingred_present = True
                if ingred_present: break
            if ingred_present: extr_ingr.append(f'✦  {i} - {ingred_amounts[i]["amount"]} {ingred_amounts[i]["measure"]}')
        output = '\n'.join(["These are the measures for the ingredients you mentioned:"] + extr_ingr) \
            if len(extr_ingr) > 0 else 'No ingredients mentioned'
    elif("when was used" in input_str):
        ingred_names = [ingredients[t]['name'] for t in ingredients]
        ingred_usage = {ingredients[t]['name']:ingredients[t]['used_in_step'] for t in ingredients}
        extr_ingr = []
        for id, i in enumerate(ingred_names):
            ingred_present = False
            for w in i.split(' '):
                if w in input_str: ingred_present = True
                if ingred_present: break
            if ingred_present: extr_ingr.append(f'✦  {i} - used in steps: {", ".join([str(t) for t in ingred_usage[i]])}')
        output = '\n'.join(["The are the steps ingredients you mentioned were used in:"] + extr_ingr) \
            if len(extr_ingr) > 0 else 'No ingredients mentioned'


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
   
    elif("what tools" in input_str or "what supplies" in input_str):
        print('You will need the following supplies:')
        for tool in instruction_full['tools']:
            print(tool)


    elif("what is" in input_str):
        print("I'm not sure, but here is a google link that might help.")
        output = google_search_query(input_str)
    elif("how do" in input_str):
        print("I'm not sure, but here is a google link that might help.")
        output = google_search_query(input_str,youtube=True)
    
    #Transformations
    elif("healthy" in input_str or "healthier" in input_str):
        print(f"OK, I will try to replace all some ingredients with healthier alternatives.")
        print('If you want more information about these new ingredients, ask and I can create a google link that could help!')
        output ='Making it healthier...'
    elif("vegetarian" in input_str):
        print("OK, I will try to replace all the meat with vegetarian alternatives. Keep in mind that these new foods may need to be prepared differently.")
        print('If you want more information about these new ingredients, ask and I can create a google link that could help!')
        output ='Making it vegatarian...'
    return new_ptr, input_str, output
    

def exact_ingredient_extraction(ingredients_el):
    return [t.replace('_', ' ') for t in presaved_ingredients if t.replace('_', ' ') in ingredients_el]
def separate_ingredients(ingredients, instructions):
    separated_ingredients = {} # it will have structure: {ingredients[i]: {"name": extracted_name, "info": {"amount":..., "measure":..., "prep":...}, "used_in_step":...}
    
    for element in ingredients:
        ingred_info, name = get_ingred(element)
        separated_ingredients[element] = {"name": name, "info": ingred_info, "used_in_step":[]}
        tmp = []
        for instr_step_id in range(len(instructions)):
            instr_step = instructions[instr_step_id]['text']
            ingred_present = False
            for w in name.split(' '):
                if w in instr_step.lower(): ingred_present = True
                if ingred_present: break
            if ingred_present: tmp.append(instr_step_id + 1)
        separated_ingredients[element]['used_in_step'] = tmp
    return separated_ingredients
def session():
    url = input("Please type the URL of the recipe: ") 
    #url = 'https://www.foodnetwork.com/recipes/banana-bread-recipe-1969572' #DEBUG
    recipe = get_recipe_info(url)
    title = recipe['title']
    ingredients = recipe['ingredients']
    
    # exact_ingredient = [exact_ingredient_extraction(el) for el in ingredients]
    instructions = recipe['instructions']
    # info = get_recipe_info(url)
    instructions = process_instructions(instructions,recipe)
    separated_ingredients = separate_ingredients(ingredients, instructions)
    print(f'Let\' get started on {title}. How would you like to start?')
    while(True):
        choice = input('[1] Recipes or [2] Ingredients: ')
        if('ingred' not in choice and '2' not in choice):
            print("Let\' get started with the recipe. When you are ready to go to the next step please input the word 'continue'")
            break
        else:
            for key in separated_ingredients.keys():
                if(separated_ingredients[key]['info']['measure']):
                    measure = separated_ingredients[key]['info']['measure']
                else:
                    measure = ''
                print(f'✧ {separated_ingredients[key]["info"]["amount"]} {measure} {separated_ingredients[key]["name"]}') #✧ - not used; ✦ - used
            print("Let\' get started with the recipe. When you are ready to go to the next step please input the word 'continue'")
            # print(ingredients)
            break
    instr_ptr = 0
    last_instr = None
    while(True):
        print(f'{instr_ptr+1}: {instructions[instr_ptr]["text"]}')
        output = ''
        input_str = input(":")
        instr_ptr, last_instr, output = parse_question(input_str, instr_ptr, last_instr, 
                                                       instructions[instr_ptr], 
                                                       separated_ingredients
                                                       )
        print(f'{output}')
        if( 'Making it vegatarian...' in output):
            instructions, separated_ingredients = transform(instructions, separated_ingredients, meat_subs)
        elif('Making it healthier...' in output):
            instructions, separated_ingredients = transform(instructions, separated_ingredients, health_subs)
            
        

    
    
if __name__ == "__main__":
    session()

