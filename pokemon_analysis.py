
#task 1 lets extract the data from the api
import requests
import argparse
from collections import Counter
import asyncio
import aiohttp
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from dash import Dash, dcc, html, State
from dash.dependencies import Input, Output
import plotly.express as px
from scipy.stats import norm
import plotly.graph_objects as go
pokemon_cache ={}
type_cache ={}
#pokemon info
pokemon_api_base = 'https://pokeapi.co/api/v2/pokemon/'
type_api_url ='https://pokeapi.co/api/v2/type/'
    
#okay so lets 
TYPE_COLORS ={
    'normal': '#A8A77A',
    'fire': '#EE8130',
    'water': '#6390F0',
    'electric':'#F7D02C',
    'grass':'#7AC74C',
    'ice':'#96D9D6',
    'fighting':'#C22E28',
    'poison':'#A33EA1',
    'ground':'#E2BF65',
    'flying':'#A98FF3',
    'psychic':'#F95587',
    'bug':'#A6B91A',
    'rock':'#B6A136',
    'ghost':'#735797',
    'dragon':'#6F35FC',
    'dark':'#705746',
    'steel':'#B7B7CE',
    'fairy':'#D685AD'
}
def create_type_badge(type_name):
    color = TYPE_COLORS.get(type_name.lower(), '#777777')

    return html.Span(
        type_name.upper(),
        className="px-3 py-1 mr-2 mb-2 rounded-full text-xs font-bold text-white shadow-md tracking-wider transmission duration-300 transform hover:scale-105",
        style={
            'backgroundColor':color,
            'fontFamily':'Inter, sans-serif'
        }
    )

def create_weakness_badge(type_name, count):
    color = TYPE_COLORS.get(type_name.lower(), '#777777')
    return html.Div(
        f"{type_name.capitalize()} (Weak to {count}x Pokemon)",
        className="p-3 m-2 rounded-lg text-white font-bold text-sm shadow-inner transition duration-300 hover:opacity-90",
        style={
            'backgroundColor':color,
            'flexgrow':1,
            'minWidth':'150px',
            'textAlign':'center'
        }
    )
def pokemon_api(pokemon_name):
    name = pokemon_name.lower()
    if name in pokemon_cache: #checks to see if the pokemon isnt already listed, if so just return w/o running api
        return(pokemon_cache[name])
    response = requests.get(pokemon_api_base+ name)
    if response.ok:
        data = response.json()
        pokemon_data ={
            'ID': data['id'],
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
        tasks = [get_pokemon_stats(session, name) for name in pokemon_names]

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
    legend_items =[
        {'name': 'Mean','color':'green'},
        {'name': 'One Standard Deviation','color':'purple'},
        {'name':f"{poke_name}'s Stat",'color':'cyan'}
    ]
    for stats in categories:
        stat_mean = round(data[stats].mean(),2)
        stat_std = round(data[stats].std(),2)
        zscore = (poke_stat[stats]- stat_mean)/stat_std

        percentile = norm.cdf(zscore) *100
        percentile_str = f"{percentile:.2f}%"
        fig =px.histogram(
                    data, 
                    x= stats, 
                    color_discrete_sequence = ['grey'], 
                    title = f"{poke_name}'s {stats}'s Stat Distribution",
                    labels ={'x': f"Base {stats} Distribution", 'y':f'Frequency'})
        fig.update_xaxes(range=[0, None])
        
        fig.add_vline(
            x= stat_mean,
            line_dash = "solid",
            line_color ="green",
            annotation_text = f"Mean: {stat_mean}",
            annotation_position = 'top',
            annotation_font_color = 'green'
        )
        fig.add_vline(
            x = poke_stat[stats],
            line_dash = 'dash',
            line_color = "cyan",
            annotation_text = f"{poke_name}'s {stats} ({percentile_str} percentile)",
            annotation_position = 'bottom right',
            annotation_font_color ='cyan'
        )
        fig.add_vline(
            x = stat_mean - stat_std,
            line_dash = 'solid',
            line_color = "purple",
            annotation_text = f"16th Percentile",
            annotation_position = 'top',
            annotation_font_color ='purple'
        )
        fig.add_vline(
            x = stat_mean +stat_std,
            line_dash = 'solid',
            line_color = "purple",
            annotation_text = f"84th Percentile",
            annotation_position = 'top',
            annotation_font_color ='purple'
        )
        fig.update_layout(showlegend = True)
        graph_list.append(fig)
        
    if graph_list:
            first_fig = graph_list[0]
            for item in legend_items:
                first_fig.add_trace(go.Scatter(
                    x =[None],
                    y= [None],
                    mode ='lines',
                    line =dict(color=item['color'],width =2),
                    name =item['name'])
                )
            first_fig.update_layout(showlegend =True)
    return(graph_list)



app = Dash(__name__, external_stylesheets= ['https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css'])

    

app.layout = html.Div(children=[
    html.H1("Pokemon Team Analyzer",
            style ={
                'textAlign':'center',
                'fontSize': '2.5em'
            }),
    html.P("Welcome to the Pokémon Team Analyzer. Build your perfect team and instantly receive a comprehensive strategic breakdown, including type coverage analysis and individual Pokémon stat distributions relative to any generation!"),
    html.P("Gain a strategic edge with individual stat distribution charts. For any selected Pokémon, you can instantly see its base stats compared against the chosen generation's mean and standard deviation, allowing you to quickly assess its competitive viability and rank (percentile) within that population."),
    html.P("Please enter up to six Pokemon. Once ready, please click 'Set Team':",
           style ={
               'font-weight':'bold'
           }),
    html.Div(style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'center'},
    children=[
        dcc.Input(id ='poke-input1', type ='text', placeholder= 'Pokemon 1', style ={'margin':'5px'}),
        dcc.Input(id = 'poke-input2', type ='text', placeholder ='Pokemon 2', style ={'margin': '5px'}),
        dcc.Input(id ='poke-input3', type = 'text', placeholder = 'Pokemon 3', style ={'margin': '5px'}),
        dcc.Input(id = 'poke-input4', type ='text',placeholder = 'Pokemon 4', style ={'margin':'5px'}),
        dcc.Input(id = 'poke-input5', type = 'text', placeholder ='Pokemon 5', style ={'margin':'5px'}),
        dcc.Input(id ='poke-input6', type = 'text', placeholder = 'Pokemon 6', style ={'margin':'5px'}),
    ]),

    html.Button('Set Team', id = 'set-team-button', n_clicks = 0, style ={'margin':'10px'}),
    html.Div(id = 'result-output'),

    html.H2("Team Type Analysis (Coverage and Weaknesses)", 
            className="text-3xl font-bold text-center text-blue-700 mt-8 mb-4 border-b-2 border-blue-300 pb-2"),
    
    html.Div(className="bg-white p-6 rounded-xl shadow-lg mb-8", children=[
        # Displays unique types covered
        html.Div(id='team-overview-display', className="mb-6 border-b pb-4"), 
        # Displays critical shared weaknesses
        html.Div(id='shared-weakness-output'), 
    ]),
    
    
    
    html.H2("Individual Stat Distribution Analysis", 
            className="text-3xl font-bold text-center text-blue-700 mt-8 mb-4 border-b-2 border-blue-300 pb-2"),
    
    html.Div(className="bg-white p-6 rounded-xl shadow-lg mb-8", children=[
        html.P('Please choose a generation to analyze your team with:',
            className="font-bold text-lg text-blue-600 mb-2"),
        dcc.Dropdown(
            id ='generation_number',
            options =[{'label':f'Generation {i}', 'value':i,} for i in range(1,10)],
            value = 1,
            className="shadow-sm mb-4"
        ),
        dcc.Store(id ='current-generation-store'),
        
        html.P("Please choose a pokemon from your set team for insight!",
            className="font-bold text-lg text-blue-600 mb-2"),
        dcc.Dropdown(
            id ='pokemon-dropdown',
            options =[], value =None,
            placeholder="Select a Pokémon...",
            className="shadow-sm"
        ),
    ]),
    
    dcc.Store(id ='team-data-store'),
    dcc.Store(id='team-analysis-store'), # Stored team analysis data
    
    # Graphs Container
    html.Div(className='flex flex-wrap -mx-2', children=[
        dcc.Graph(id='hp-graph', className='w-full lg:w-1/3 p-2'),
        dcc.Graph(id='attack-graph', className='w-full lg:w-1/3 p-2'),
        dcc.Graph(id='defense-graph', className='w-full lg:w-1/3 p-2'),
        dcc.Graph(id='special-attack-graph', className='w-full lg:w-1/3 p-2'),
        dcc.Graph(id='special-defense-graph', className='w-full lg:w-1/3 p-2'),
        dcc.Graph(id='speed-graph', className='w-full lg:w-1/3 p-2')
    ])
])

@app.callback(
    Output('pokemon-dropdown', 'options'),
    Output('team-data-store','data'),
    Output('result-output','children'),
    Output('team-analysis-store','data'),
    Input('set-team-button','n_clicks'),
    State('poke-input1','value'),
    State('poke-input2','value'),
    State('poke-input3','value'),
    State('poke-input4','value'),
    State('poke-input5','value'),
    State('poke-input6','value'),
)
def update_team(n_clicks, poke1, poke2,poke3, poke4, poke5, poke6):
    if n_clicks is None or n_clicks ==0:
        return[],{}, "Team is ready for analysis.", {}
    input_names = [name.strip() for name in [poke1, poke2, poke3,poke4, poke5, poke6] if name and name.strip()]

    if not input_names:
        return [],{}, "Please enter at least one Pokemon name.", {}
    user_team = team_builder(input_names)
    valid_team_names = [p['Name'].capitalize() for p in user_team.values()]
    if not valid_team_names:
        return [],{}, "Error: Could not retrieve data for any Pokemon. Check Spelling.", {}
    team_info= team_analyzer(user_team)
    new_options = [{'label':name,'value':name} for name in valid_team_names]

    team_info_serializable = {
        k: dict(v) if isinstance(v, Counter) else v 
        for k, v in team_info.items()
    }

    return(
        new_options,
        user_team,
        html.Span([
            "Team updated successfully: ",
            html.Span(', '.join(valid_team_names), className="font-extrabold text-green-700")
        ]),
        team_info_serializable
    )
@app.callback(
    Output('team-overview-display', 'children'),
    Output('shared-weakness-output', 'children'),
    Input('team-analysis-store', 'data'),
    prevent_initial_call=True
)
def update_team_analysis_displays(team_analysis_data):
    if not team_analysis_data or not team_analysis_data.get('overall_types'):
        return (
            html.P("Enter your team above to see the unique types covered.", className="text-center text-gray-500"),
            html.P("No team data available for weakness analysis.", className="text-center text-gray-500")
        )


    overall_types_list = team_analysis_data.get('overall_types', [])
    type_badges = [create_type_badge(poke_type) for poke_type in overall_types_list]
    
    overall_types_content = html.Div(className="text-center", children=[
        html.H3("Unique Type Coverage in Team", className="text-xl font-semibold mb-3 text-blue-800"),
        html.P(f"Your team covers **{len(overall_types_list)}** unique types out of the 18 available types."),
        html.Div(type_badges, className='flex flex-wrap justify-center my-4'),
    ])

    weakness_types_dict = team_analysis_data.get('shared_weaknesses', {})
    
    
    critical_weaknesses = {k: v for k, v in weakness_types_dict.items() if v >= 3}
    
    sorted_shared_weakness = sorted(
        critical_weaknesses.items(),
        key=lambda item: item[1],
        reverse=True
    )
    weakness_badges = [create_weakness_badge(type_name, count) for type_name, count in sorted_shared_weakness]

    if not weakness_badges:
        weakness_content = html.Div(className="p-4 bg-green-50 rounded-lg border border-green-200", children=[
            html.P("Excellent! Your team has **no critical overlapping weaknesses** (fewer than 3 Pokémon have a combined 2x or 4x weakness to the same type).",
                   className="text-center font-bold text-green-700")
        ])
    else:
        weakness_content = html.Div(className="p-4 bg-red-50 rounded-lg border border-red-200", children=[
            html.P("Warning! The following types are **critical shared weaknesses** for 3 or more of your Pokémon (based on cumulative 2x and 4x counts). Consider revising your team composition.",
                   className="text-center font-bold text-red-700 mb-4"),
            html.Div(weakness_badges, className='flex flex-wrap justify-center')
        ])

    return overall_types_content, weakness_content
@app.callback(
    Output('hp-graph','figure'),
    Output('attack-graph','figure'),
    Output('defense-graph','figure'),
    Output('special-attack-graph', 'figure'),
    Output('special-defense-graph', 'figure'),
    Output('speed-graph','figure'),
    Input('pokemon-dropdown','value'),
    State('team-data-store','data'),
    Input('current-generation-store','data'),
    prevent_initial_call = True
    
)
def update_stat_graphs(selected_poke_name,my_team, gen_pop_data):
    def get_blank_fig(title="Select a Pokémon and Generation for Stat Analysis"):
        return px.bar(pd.DataFrame({'x': [0], 'y': [0]})).update_layout(
            title=title,
            xaxis_visible=False, yaxis_visible=False, 
            annotations=[dict(text="No data selected", showarrow=False, xref="paper", yref="paper", x=0.5, y=0.5)],
            margin=dict(t=50, b=20),
            font={'family': 'Inter, sans-serif'}
        )

    if not selected_poke_name or not my_team or not gen_pop_data:
        # Return 6 blank figures
        return (get_blank_fig(),) * 6
    
    try:
        pokemon_data = my_team[selected_poke_name.lower()]
    except KeyError:
        return (get_blank_fig(f"Error: {selected_poke_name} data not found in team store."),) * 6

    gen_df = pd.DataFrame(gen_pop_data)
    all_figures = create_stat_graph(gen_df, selected_poke_name,pokemon_data['Stats'])

    return tuple(all_figures)

@app.callback(
    Output('current-generation-store','data'),
    Input('generation_number', 'value'),

)
def update_population(gen_number):
    if not gen_number:
        return(
            pd.DataFrame().to_dict('list')
        )
    pop_names = generation_pokemon(gen_number)
    pop_stats = asyncio.run(get_all_pokemon_data(pop_names))
    results = data_builder(pop_stats)
    return(results.to_dict('list'))

if __name__ == "__main__":
    app.run(debug= True)
    '''
    for pokemon_name, pokemon_stat in my_team.items():
        all_poke_graphs =create_stat_graph(results,pokemon_name, pokemon_stat['Stats'])
        for graph_fog in all_poke_graphs:
            plt.show()
    '''