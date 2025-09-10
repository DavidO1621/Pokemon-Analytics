#task 1 lets extract the data from the api
import requests
import argparse
from collections import Counter
pokemon_cache ={}
type_cache ={}
#pokemon info
pokemon_api_base = 'https://pokeapi.co/api/v2/pokemon/'
type_api_url ='https://pokeapi.co/api/v2/type/'
    


def pokemon_api(pokemon_name):
    name = pokemon_name.lower()
    if name in pokemon_cache: #checks to see if the pokemon isnt already listed, if so just return w/o running api
        return(pokemon_cache[name])
    response = requests.get(pokemon_api_base+ name)
    if response.ok:
        data = response.json()
        pokemon_data ={
            'Name': data['name'],
            'Types': [t["type"]["name"] for t in data["types"]],
            'Stats': {stat['stat']['name']: stat['base_stat'] for stat in data['stats']},
            'Abilities': [ab['ability']['name'] for ab in data['abilities']]
        }
        pokemon_cache[name]= pokemon_data
        return(pokemon_data)
    else:
        print(f"Error! {pokemon_name} does not exist. Please check spelling or provide proper Pokemon name!")
        print(f"The status code is {response.status_code}")
        return(None)
    
def get_type_data(input):
    type = input.lower()
    if type in type_cache:
        return(type_cache[type])
    
    response = requests.get(type_api_url + type)
    if not response.ok:
        print(f"Type is wrong! Please check input")
        return(None)
    data = response.json()
    type_cache[type]= data

    return(data)

def type_analysis(pokemon):
    poke_data =pokemon_api(pokemon)
    poke_data['Weaknesses']=[]
    poke_data['Strong_Against']=[]
    poke_data['Resistance']=[]
    poke_data['Immunity']=[]
    poke_data['No_effect_on']=[]
    for type in poke_data['Types']:
        data = get_type_data(type)

        data_relations = data.get('damage_relations',{})
        #weaknesses
        weaknesses =[w['name'] for w in data_relations.get('double_damage_from',[])]
        poke_data['Weaknesses'].extend(weaknesses)
        #strengths
        strengths = [s['name'] for s in data_relations.get('double_damage_to', [])]
        poke_data['Strong_Against'].extend(strengths)
        #resistance
        resistance = [r['name'] for r in data_relations.get('half_damage_from', [])]
        poke_data['Resistance'].extend(resistance)
        #immune from
        immune = [i['name'] for i in data_relations.get('no_damage_from',[])]
        poke_data['Immunity'].extend(immune)
        #no effect on
        no_effect = [n['name'] for n in data_relations.get('no_damage_to', [])]
        poke_data['No_effect_on'].extend(no_effect)

    return(poke_data)
#now see where each weakness stands ex 2x, 4x effective
def type_calculator(pokemon):
    poke_data = type_analysis(pokemon)
    poke_data['Damage_Multiplier']={
        'normal': 1.0,
        'fire': 1.0,
        'water':1.0,
        'electric': 1.0,
        'grass':1.0,
        'ice':1.0,
        'fighting':1.0,
        'poison':1.0,
        'ground':1.0,
        'flying': 1.0,
        'psychic': 1.0,
        'bug': 1.0,
        'rock':1.0,
        'ghost':1.0,
        'dragon':1.0,
        'dark':1.0,
        'steel':1.0,
        'fairy':1.0
    }

    effects ={
        'Weaknesses':2.0,
        'Resistance':0.5,
        'Immunity':0.0
    }

    for category, factor in effects.items():
        for type in poke_data[category]:
            poke_data['Damage_Multiplier'][type]*=factor

    #print(data)
    
    #we have weakness, immunities, resistances
    return(poke_data)
        
#accepts input from user
def pick_team():
    team=[]
    while len(team) < 6:
        name = input(f"Enter Pokemon {len(team)+1 } or 'done' when ready: ").lower()
        if name == 'done':
            break
        team.append(name)
    print(team)
    return(team)
    
def team_builder(team):
    #accepts a list of 6 pokemon and return a list of all the details of the 6 pokemon
    pokemon_team={}
    if len(team)> 6:
        (print(f'The pokemon list exceeds 6! Please only provide 6 or less!'))
        return None
    for pokemon in team:
        poke_info =type_calculator(pokemon)
        pokemon_team[poke_info['Name']]= poke_info
        
    return(pokemon_team)

def categorize_role(stats):
    bank ={}
    bank['Physical_Sweeper']= stats['attack']*1.2 + stats['speed']
    bank['Special_Sweeper']= stats['speed'] + stats['special-attack']*1.2
    bank['Tank']= (stats['defense'] + stats['special-defense'] + stats['attack'] + stats['special-attack'])*0.5
    bank['Wall']= (stats['defense'] + stats['special-defense'] + stats['hp'])*(2/3)
    print(bank)
    max_item = max(bank.items(), key = lambda x:x[1])

    if max_item[1] < 150:
        return('Support', max_item[1])
    return(max_item)

    
#this should analyze the team's covered areas like weaknesses, strenghts, resistances. 
# it should also keep a tally of certain groups to see not so many pokemon have overlapping types

def team_analyzer(team):
    team_info ={}
    team_info['overall_types']=[]
    team_info['shared_types']={}
    team_info['shared_weaknesses']=[]
    team_info['shared_resistances']=[]
    team_info['roles']={}

    categories = ['shared_types','shared_weaknesses','shared_resistances']
    for pokemon in team:
        data1 = team[pokemon]['Types']
        data2 = team[pokemon]['Weaknesses']
        data3= team[pokemon]['Resistance']
        team_info['overall_types'].extend(data1)
        team_info['shared_weaknesses'].extend(data2)
        team_info['shared_resistances'].extend(data3)
        #print(team[pokemon]['Stats'])
        team_info['roles'][pokemon]= categorize_role(team[pokemon]['Stats'])



    team_info['shared_types']= Counter(team_info['overall_types'])
    team_info['shared_weaknesses'] = Counter(team_info['shared_weaknesses'])
    team_info['shared_resistances'] = Counter(team_info['shared_resistances'])

    '''
    for type in team_info['overall_types']:
        if type not in team_info['shared_types']:
            team_info['shared_types'][type]= 1
        else:
            team_info['shared_types'][type] +=1
    '''
    team_info['overall_types']= set(team_info['overall_types'])
    #team_info['shared_types']= set(team_info['shared_types'])
    team_info['shared_weaknesses']= set(team_info['shared_weaknesses'])
    print(team_info)
if __name__ == "__main__":
    #print(pokemon_api('heracross'))
    #print(type_analysis('haunter'))

    #print(type_calculator('blastoise'))
    my_team = team_builder(['blastoise', 'snorlax','charizard','blissey','zapdos','mewtwo'])
    team_stats = team_analyzer(my_team)
#def main():
'''
def team_analyzer(team):
    all_types = get_all_types(team)
    shared_types = find_shared_items(team, 'Types')
    # and so on...
    
    return {'overall_types': all_types, 'shared_types': shared_types}

def get_all_types(team):
    overall_types = []
    for pokemon in team:
        overall_types.extend(team[pokemon]['Types'])
    return set(overall_types)

'''
