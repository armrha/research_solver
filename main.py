from copy import deepcopy
import re
import os

def T_BOARD(name):
    if "T_BOARD(" in name:
        adjust_name = name.split('T_BOARD("')[1]
        adjust_name = adjust_name.split('")')[0]
        return f"circuit board ({adjust_name})"
    else:
        if "T_BOARD_MECHA(" in name:
            adjust_name = name.split('T_BOARD_MECHA("')[1]
            adjust_name = adjust_name.split('")')[0]
            return f"exosuit module circuit board ({adjust_name})"
        return name

def name_cleaning(source_line):
    item_name = source_line.split('=', 1)[1].strip()
    if item_name.startswith('"') and item_name.endswith('"'):
        item_name = item_name[1:-1]
    else:
        item_name = T_BOARD(item_name)
    return item_name

def comment_remover(text):
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return " "
        else:
            return s
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(pattern, replacer, text)

def list_reader(listed_items):
    ret = {}
    listed_items = listed_items.split('=', 1)[1].strip()
    if "rand" in listed_items:
        #don't even bother trying to solve for that for now
        return ret
    if "list(" in listed_items:
        items_to_map = listed_items.split('list(')[1]
        items_to_map = items_to_map.split(')')[0]
        items_sep = items_to_map.split(',')
        for item in items_sep:
            breaking = item.split(' = ')
            if len(breaking) > 1:
                breaking[0] = breaking[0].strip()
                ret[breaking[0]] = int(breaking[1].strip())
    return ret

def comment_remover(text):
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return " " # note: a space and not an empty string
        else:
            return s
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(pattern, replacer, text)

def gather_items(path):
    ret = []
    for root, dirs, files in os.walk(path):
        root_split = root.split(os.sep)
        root_split.pop(0)
        for file in files:
            if (".dm" in file and ".dme" not in file and ".dmi" not in file and ".dmb" not in file):
                file_path = root + os.sep + file
                read_str = open(file_path, "r")
                data = read_str.read()
                read_str.close()
                data = comment_remover(data)
                clear_whitespace_regex = r"^[\t\s]*$\n(?!^/)"
                data = re.sub(clear_whitespace_regex, '', data, flags=re.M)
                extract_regex = r"^\/[\s\S]*?(?=\r?\n\r?\s?\n|\Z)"
                matches = re.finditer(extract_regex, data, re.MULTILINE)
                for val, match in enumerate(matches):
                    ret.append(match.group(0))
    return ret

def deconstruct_item(points, levels_original, name=None):
    levels = deepcopy(levels_original)
    for item in points:
        if(points[item] > 0): #Ignore no-techs
            levels[item][1] += points[item]
            while levels[item][1] >= (5 ** levels[item][0]):
                levels[item][0] += 1
    return levels

def materials_recurse(designs, item):
    if "/" in item:
        parent = "/".join(item.split('/')[0:-1])
        if parent in designs and 'materials' in designs[parent]:
            return designs[parent]['materials']
        else:
            return materials_recurse(designs, parent)
    else:
        return None

def calculate_winner(printable_designs, levels):
    score = 0
    current_winner = None
    winning_points = {'TECH_MATERIAL': 0, 'TECH_ENGINEERING': 0, 'TECH_MAGNET': 0, 'TECH_PHORON': 0,
                           'TECH_POWER': 0, 'TECH_BIO': 0, 'TECH_BLUESPACE': 0, 'TECH_COMBAT': 0, 'TECH_DATA': 0,
                           'TECH_ARCANE': 0, 'TECH_ILLEGAL': 0}
    for design in printable_designs:
        buildable = 1
        points_for_item = {'TECH_MATERIAL': 0, 'TECH_ENGINEERING': 0, 'TECH_MAGNET': 0, 'TECH_PHORON': 0,
                           'TECH_POWER': 0, 'TECH_BIO': 0, 'TECH_BLUESPACE': 0, 'TECH_COMBAT': 0, 'TECH_DATA': 0,
                           'TECH_ARCANE': 0, 'TECH_ILLEGAL': 0}
        for tech in design['req_tech']:
            if design['req_tech'][tech] > levels[tech][0]:
                #Disqualified from competition
                buildable = 0
        if buildable == 1:
            for tech in design['origin_tech']:
                points_for_item[tech] = 5 ** design['origin_tech'][tech]
            contender_levels = deconstruct_item(points_for_item, levels)
            champion_levels = deconstruct_item(winning_points, levels)
            #Prioritize largest spread of levels per item
            contender = 0
            champion = 0
            for tech_adv in contender_levels:
                if contender_levels[tech_adv][0] > levels[tech_adv][0]:
                    contender += 1
            for tech_adv in champion_levels:
                if champion_levels[tech_adv][0] > levels[tech_adv][0]:
                    champion += 1
            if(contender == champion):
                #No reach difference, so let's go by total levels
                contender = sum([v[0] for v in contender_levels.values()])
                champion = sum([v[0] for v in champion_levels.values()])
            if(contender == champion):
                #Tied! Check which gives the most points across variety... maybe not worth it
                contender = 0
                champion = 0
                for techname in  contender_levels:
                    if contender_levels[techname][1] > levels[techname][1]:
                        if contender_levels[techname][0] == (levels[techname][0] -1):
                            contender += 1
                for techname in  champion_levels:
                    if champion_levels[techname][1] > levels[techname][1]:
                        if champion_levels[techname][0] == (levels[techname][0] - 1):
                            champion += 1
            if(contender == champion):
                #Tied! Check which gives the most total points
                contender = sum([v[1] for v in contender_levels.values()])
                champion = sum([v[1] for v in champion_levels.values()])

            if(contender > champion):
                current_winner = design
                winning_points = points_for_item
    return current_winner, winning_points

def printable_collection(sources_orig, designs_orig, mat_restriction=None):
    #Put anything you don't want to use in here... stuff that doesn't exist, etc
    blacklist = ['integrated circuit printer upgrade disk - circuit cloner']

    printable_designs = []
    if mat_restriction is None:
        mat_restriction = []
    sources = deepcopy(sources_orig)
    designs = deepcopy(designs_orig)
    for item in designs:
        if 'build_path' in designs[item]:
            datum = designs[item]['build_path']
            datum = datum.lower()
            if datum in sources:
                #If there's no req tech, probably just a materials def, ignore it for now
                if 'req_tech' in designs[item]:
                    sources[datum]['req_tech'] = designs[item]['req_tech']
                    if 'name' in sources[datum] and sources[datum]['name'] not in blacklist:
                        if 'mechfab' not in item:
                            if mat_restriction:
                                if 'materials' not in designs[item]:
                                    #Probably up a bit from here
                                    designs[item]['materials'] = materials_recurse(designs, item)
                                if 'materials' in designs[item] and designs[item]['materials'] is not None:
                                    if all(elem in mat_restriction for elem in list(designs[item]['materials'].keys())):
                                        sources[datum]['materials'] = designs[item]['materials']
                                        printable_designs.append(sources[datum])
                            else:
                                printable_designs.append(sources[datum])
    #Special provision for the portable integrated circuit printer...
    printer_req_tech = designs['/datum/design/item/integrated_electronics/custom_circuit_printer']['req_tech']
    for item in sources:
        if 'integrated' in item:
            sources[item]['req_tech'] = printer_req_tech
            #Don't add bogus items...
            if 'name' in sources[item] and sources[item]['name'] not in blacklist:
                printable_designs.append(sources[item])
    return printable_designs

def reset_levels():
    return { 'TECH_MATERIAL': [3, 0] , 'TECH_ENGINEERING': [3, 0], 'TECH_MAGNET': [3, 0], 'TECH_PHORON': [3, 0], 'TECH_POWER': [3, 0], 'TECH_BIO': [3, 0], 'TECH_BLUESPACE': [3, 0], 'TECH_COMBAT': [3, 0], 'TECH_DATA': [3, 0], 'TECH_ARCANE': [0, 0], 'TECH_ILLEGAL': [0, 0]}


def solve_research(path):
    levels = reset_levels()
    os.chdir(path)
    include = ['.\\code\\defines\\obj\\', '.\\code\\game\\objects', '.\\code\\game\\objects\\items', '.\\code\\game\\gamemodes','.\\code\\game\\machinery', '.\\code\\modules']
    designs = {}
    sources = {}
    for dirname in include:
        ret = gather_items(dirname)
        for match in ret:
            if 'origin_tech = ' in match:
                origin_item_lines = match.splitlines()
                datum = origin_item_lines[0]
                sources[datum] = {}
                for oi in origin_item_lines:
                    if "name = " in oi and not 'build_name' in oi:
                        sources[datum]['name'] = name_cleaning(oi)
                    if "origin_tech = " in oi and 'list(' in oi:
                        if ')' not in oi:
                            list_compactor_regex  = r"origin_tech = list\([^)]+?\)"
                            list_to_compact  = re.finditer(list_compactor_regex, match, re.MULTILINE)
                            for list_match in list_to_compact:
                                line_to_read =  " ".join((list_match.group().split()))
                            sources[datum]['origin_tech'] = list_reader(line_to_read)
                        else:
                            sources[datum]['origin_tech'] = list_reader(oi)

            if 'req_tech = ' in match or 'materials = ' in match:
                design_item_lines = match.splitlines()
                datum = design_item_lines[0]
                designs[datum] = {}
                for oi in design_item_lines:
                    if "name = " in oi:
                        designs[datum]['name'] = name_cleaning(oi)
                    if "build_path = " in oi:
                        designs[datum]['build_path'] = oi.split('=')[1].strip()
                    if "req_tech = " in oi and 'list(' in oi:
                        if ')' not in oi:
                            list_compactor_regex  = r"origin_tech = list\([^)]+?\)"
                            list_to_compact  = re.finditer(list_compactor_regex, match, re.MULTILINE)
                            for list_match in list_to_compact:
                                line_to_read =  " ".join((list_match.group().split()))
                            sources[datum]['origin_tech'] = list_reader(line_to_read)
                        else:
                            designs[datum]['req_tech'] = list_reader(oi)
                    if "materials = " in oi and 'list(' in oi and ')' in oi:
                        designs[datum]['materials'] = list_reader(oi)

    printable_designs = printable_collection(sources, designs)

    #TODO: Add autolathe designs, just in case...

    print("Without mats...")
    increasing = 1
    while increasing:
        last_value = increasing
        winner, points = calculate_winner(printable_designs, levels)
        levels = deconstruct_item( points, levels )
        print(winner['name'])
        increasing = sum([v[0] for v in levels.values()])
        if last_value == increasing:
            #Probably done
            increasing = None
    levels = reset_levels()
    printable_designs = printable_collection(sources, designs, ['DEFAULT_WALL_MATERIAL','MATERIAL_GLASS','MATERIAL_STEEL'])
    print("With default mats... (steel / glass)")
    increasing = 1
    while increasing:
        last_value = increasing
        winner, points = calculate_winner(printable_designs, levels)
        levels = deconstruct_item( points, levels )
        print(winner['name'])
        increasing = sum([v[0] for v in levels.values()])
        if last_value == increasing:
            #Probably done
            increasing = None

    print(levels)

if __name__ == '__main__':
    ##Replace with your aurora git directory
    path = "D:\\aurorastation\\"
    solve_research(path)
