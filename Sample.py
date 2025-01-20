import plotly.express as px
import requests
import json
import pandas as pd

#r = requests.get('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json')open('test.json')
f = open("test.json")
counties = json.load(f)
target_states = ['01']
counties['features'] = [f for f in counties['features'] if f['properties']['STATE'] in target_states]
print(counties)
df = pd.read_csv('fips-unemp-16.csv', dtype={'fips': str})

fig = px.choropleth(df, geojson=counties, locations='fips', color='unemp',
                    color_continuous_scale='Viridis',
                    range_color=(0, 12),
                    scope='usa',
                    labels={'unemp': 'unemployment rate'}
                    )
fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
fig.show()
