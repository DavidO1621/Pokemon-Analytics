#task 1 lets extract the data from the api
import requests
import argparse
from collections import Counter
import asyncio
import aiohttp
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
pokemon_cache ={}
type_cache ={}
#pokemon info
pokemon_api_base = 'https://pokeapi.co/api/v2/pokemon/'
type_api_url ='https://pokeapi.co/api/v2/type/'
    
#okay so lets 

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

    team_info['overall_types']= list(set(team_info['overall_types']))
    return(team_info)

async def get_all_pokemon_data(pokemon_names):
    async with aiohttp.ClientSession() as session:
        #lets break the list of pokemon names we get and feed it intot the other function one at a time
        tasks = [get_pokemon_stats(session, name) for name in poke_names]

        pokemon_data_list = await asyncio.gather(*tasks)
        return(pokemon_data_list)
    

async def get_pokemon_stats(session,pokemon_name):
    url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}'
    try:
        async with session.get(url) as response:
            data = await response.json()
            stats = {stat['stat']['name']: stat['base_stat'] for stat in data['stats']}
            return{
                'name':data['name'],
                'stats':stats
            }

    except aiohttp.ClientError as e:
        print(f'Error! Something went wrong retrieving {pokemon_name}: {e}')
    return None
    
def generation_pokemon(gen_num):
    gen_dict={
        1:'151',
        2:'251',
        3:'386',
        4:'493',
        5:'649',
        6:'721',
        7:'809',
        8:'905',
        9:'1025'
    }
    gen_url =f'https://pokeapi.co/api/v2/pokemon?limit={gen_dict[gen_num]}'
    response =requests.get(gen_url)
    if response.ok:
        data = response.json()
        pokemon_names = [p['name'] for p in data['results']]
        return(pokemon_names)
        
    else:
        print(f'Error! Please provide a proper generation!')
        return[]
        
def data_builder(data):
    #this  is where we will be dumping the pokemon's data and itll slowly create the data population
    stat_categories= ['hp','attack','special-attack','defense','special-defense','speed']
    data_pop={cat: [] for cat in stat_categories}
    for i in range(len(data)):
        for cat_name in stat_categories:
            data_pop[cat_name].append(data[i]['stats'][cat_name])
    pop_df = pd.DataFrame(data_pop)    
    return(pop_df)

def create_stat_graph(data,poke_name, poke_stat):
    categories = list(data.columns.values)
    graph_list =[]
    for stats in categories:
        stat_mean = round(data[stats].mean(),2)
        stat_std = round(data[stats].std(),2)

        fig, ax = plt.subplots()
        sns.histplot(data = data, x= stats, kde = True)

        plt.axvline(stat_mean + stat_std, color ='black', linestyle ='--', label= f'+1σ: {stat_mean + stat_std}')
        plt.axvline(stat_mean- stat_std, color ='black', linestyle ='--', label = f'-1σ: {stat_mean - stat_std}')
         #lets acces the pokemon's stats so we can place them into the graph
        pokemon_selected_stat = poke_stat[stats]
        plt.axvline(pokemon_selected_stat, color='red', linestyle='-', linewidth =2, label= f"{poke_name}: {pokemon_selected_stat} ")
        plt.title(f'Pokemon {stats} Stat Distribution')
        plt.xlabel(f'Base {stats} Stat')
        plt.ylabel(f'Frequency')
        plt.legend()
        plt.tight_layout()
        graph_list.append(fig)
    return(data.describe())
if __name__ == "__main__":



    
    my_team = team_builder(['blastoise', 'snorlax','charizard','blissey','zapdos','mewtwo'])
    team_stats = team_analyzer(my_team)
    print(my_team)

    gen_number = int(input(f'Enter the generation you want to analyze (1-9): '))
    #team = input('Please enter your team! (Teams of 6 or less): ')
    poke_names =generation_pokemon(gen_number)
    all_stats = asyncio.run(get_all_pokemon_data(poke_names))
    results = data_builder(all_stats)
    #print(results)
    for pokemon_name, pokemon_stat in my_team.items():
        print(pokemon_name)
        print(pokemon_stat['Stats'])
        all_poke_graphs =create_stat_graph(results,pokemon_name, pokemon_stat['Stats'])
        for graph_fog in all_poke_graphs:
            plt.show()
    