# Part 1: Setup and Data Extraction
import requests  # You can use this library to interact with the API
import argparse
def get_pokemon_data(pokemon_name):
    """
    Fetch data from the Pokémon API for the given Pokémon.
    :param pokemon_name: str
    :return: dict (JSON data)
    """
    main_url = "https://pokeapi.co/api/v2/pokemon/"
    response = requests.get(main_url+ pokemon_name.lower())
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error!: The pokemon doesn't", pokemon_name,"exist! The status code is ",response.status_code)
    

def extract_pokemon_info(data):
    """
    Extract the name, types, and stats of the Pokémon from the API data.
    :param data: dict (API JSON response)
    :return: dict (contains 'name', 'types', and 'stats')
    """
    pokemon_dict = {}
    pokemon_types=[]
    pokemon_dict["name"]= data["name"]
    for type in data["types"]:
        pokemon_types.append(type["type"]["name"])
    pokemon_dict["types"] = pokemon_types
    for stat in data["stats"]:
        stat_name= stat["stat"]["name"]
        stat_value = stat["base_stat"]
        pokemon_dict[stat_name]= stat_value
    return pokemon_dict

# Part 2: Data Analysis
def find_extreme_stats(stats):
    """
    Identify the highest and lowest stats of the Pokémon.
    :param stats: dict (stat names as keys and values as integers)
    :return: tuple (highest_stat, lowest_stat)
    """
    numeric_stats= {}
    max_stats={}
    min_stats={}
    for key, value in  stats.items():
        if isinstance(value, (int,float)):
            numeric_stats[key]= value


    max_stat = max(numeric_stats.items(),key = lambda item: item[1])
    for key, value in numeric_stats.items():
        if value == max_stat[1]:
            max_stats[key]= value

    min_stat = min(numeric_stats.items(),key = lambda item: item[1])
    for key, value in numeric_stats.items():
        if value == min_stat[1]:
            min_stats[key]= value
    

    return max_stats, min_stats
'''
pokemon1= get_pokemon_data("pikachu")
pokemon1_stat= extract_pokemon_info(pokemon1)
print(pokemon1_stat)
pokemon_extremas= find_extreme_stats(pokemon1_stat)
print(pokemon_extremas)
pokemon1_type= pokemon1_stat["types"]
print(pokemon1_type)
'''
def analyze_weaknesses(types):
    """
    Analyze the Pokémon's weaknesses based on its types.
    :param types: list of str (Pokémon types)
    :return: list of str (types the Pokémon is weak to)
    """
    weaknesses_dict={
        "normal": ["fighting"],
        "water":["electric", "grass"],
        "electric": ["ground"],
        "fire": ["water","rock","ground"],
        "grass":["flying","fire","bug","poison","ice"],
        "steel": ["fire","ground","fighting"],
        "dark": ["bug","fighting","fairy"],
        "fairy":["poison","steel"],
        "fighting":["flying","psychic","fairy"],
        "ice":["fire","fighting","rock","steel"],
        "dragon": ["dragon","ice","fairy"],
        "flying":["electric","ice","rock"],
        "ground":["water","grass","ice"],
        "poison":["ground","psychic"],
        "bug":["flying","fire","rock"],
        "rock":["water","grass","ground","fighting","steel"],
        "ghost":["ghost","dark"],
        "psychic":["dark","bug","ghost"]
    }
    resistance_dict={
        "grass":["grass", "water", "ground","electric"],
        "fire":["fire","ice","steel","bug","grass","fairy"],
        "water":["water","steel","ice","fire"],
        "electric":["electric","steel","flying"],
        "dragon":["water","electric","fire","grass"],
        "steel":["ice","grass","dragon","normal","fairy","rock","bug","psychic","flying","steel"],
        "psychic": ["psychic", "fighting"],
        "fighting": ["bug","rock","dark"],
        "ghost":["bug","poison"],
        "rock":["normal","fire","poison","flying"],
        "bug":["grass","fighting","ground"],
        "poison":["grass","fighting","poison","bug","fairy"],
        "ground":["poison","rock"],
        "flying":["grass","fighting","bug"],
        "ice":["ice"],
        "fairy":["fighting","bug","dark"],
        "dark":["ghost","dark"],
        "normal":["None"]
    }
    no_effect_dict={
        "normal":["ghost"],
        "ghost":["normal","fighting"],
        "flying":["ground"],
        "ground":["electric"],
        "steel":["poison"],
        "fairy":["dragon"],
        "dark":["psychic"],
        "fighting":["ghost"]
    }
    super_effective_dict={
        
        "water":["fire", "ground","rock"],
        "electric": ["flying","water"],
        "fire": ["grass","bug","steel","ice"],
        "grass":["water","ground","rock"],
        "steel": ["rock","fairy","ice"],
        "dark": ["psychic","ghost"],
        "fairy":["fighting","dragon","dark"],
        "fighting":["rock","steel","dark","normal","ice"],
        "ice":["grass","ground","flying","dragon"],
        "dragon": ["dragon"],
        "flying":["grass","fighting","bug"],
        "ground":["fire","electric","poison","rock","steel"],
        "poison":["grass","fairy"],
        "bug":["grass","psychic","dark"],
        "rock":["fire","flying","ice","bug"],
        "ghost":["ghost","psychic"],
        "psychic":["fighting","poison"]
    }
    weaknesses=[]
    for pokemons_type in types:
        if pokemons_type in weaknesses_dict:
            weaknesses.extend(weaknesses_dict[pokemons_type])
        if pokemons_type in no_effect_dict:
            for non_effect in no_effect_dict[pokemons_type]:
                if non_effect in weaknesses:
                    weaknesses.remove(non_effect)
    for pokemons_type in types:
        if pokemons_type in resistance_dict:
            for resistance_effect in resistance_dict[pokemons_type]:
                if resistance_effect in weaknesses:
                    weaknesses.remove(resistance_effect)
    
    resistant =[]
    for pokemons_type in types:
        if pokemons_type in resistance_dict:
            resistant.extend(resistance_dict[pokemons_type])
            
    for pokemons_type in types:
        if pokemons_type in weaknesses_dict:
            for effected in weaknesses_dict[pokemons_type]:
                if effected in resistant:
                    resistant.remove(effected)
    strengths =[]
    for pokemons_type in types:
        if pokemons_type in super_effective_dict:
            strengths.extend(super_effective_dict[pokemons_type])
    return(set(weaknesses), set(strengths), set(resistant))

#print(analyze_weaknesses(pokemon1_type))

# Part 3: Program Flow
def analyze_pokemon(pokemon_name):
    """
    Main function to analyze a single Pokémon by name.
    :param pokemon_name: str
    :return: None
    """
    
    #user_name= input("Hi! Welcome to my Pokemon Analysis calculator! Please tell me your name!")
    pokemon_api= get_pokemon_data(pokemon_name)
    pokemon_data= extract_pokemon_info(pokemon_api)
    max_stats, min_stats= find_extreme_stats(pokemon_data)
    pokemon_type= pokemon_data["types"]
    pokemons_weaknesses, pokemon_strengths, pokemon_resistance = analyze_weaknesses(pokemon_type)

    print(f"The Pokemon",pokemon_name," has the follwing stats\n")
    print(f"Name: {pokemon_data['name'].capitalize()}")
    print(f"Type(s): ",{' '.join(pokemon_data["types"])})
    print(f"Highest Stat(s): ",max_stats,)
    print(f"Lowest Stat(s):", min_stats)
    print(f"Strong Against:", pokemon_strengths)
    print(f"Weakness(es):", pokemons_weaknesses)
    print(f"Resistant against:", pokemon_resistance)
   
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze the following pokemon for its stats and attributes.")
    parser.add_argument("pokemon_name", type = str, help="Please provide the name of the pokemon.")
    args = parser.parse_args()

    analyze_pokemon(args.pokemon_name)