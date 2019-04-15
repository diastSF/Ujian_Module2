import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from plotly import tools
import plotly.graph_objs as go
import pandas as pd
import requests
import numpy as np
import dash_table as dt
from sqlalchemy import create_engine


app = dash.Dash(__name__)

engine = create_engine('mysql+mysqlconnector://root:diast050209@localhost/titanic?host=localhost?port=3306')
conn = engine.connect()

titanic = conn.execute('SELECT * from titanic').fetchall()
dfTitanic = pd.DataFrame(titanic, columns='survived pclass sex age sibsp parch fare embarked class who adult_male deck embark_town alive alone outliercalid outlier'.split())

def generate_table(dataframe, pagesize=10):
    return dt.DataTable(
        id='table-multicol-sorting',
        columns=[
            {"name": i, "id": i} for i in dataframe.columns
        ],
        pagination_settings={
            'current_page': 0,
            'page_size': pagesize
        },
        pagination_mode='be',
        style_table={'overflowX': 'scroll'},
        sorting='be',
        sorting_type='multi',
        sorting_settings=[]
    )

app.title = 'Dashboard Titanic'

app.layout = html.Div([
    html.H1('Dashboard Pokemon'),
    html.H3('Created by : Diast S. Fiddin'),
    dcc.Tabs(id='Tabs', value='tab-1', children=[
        dcc.Tab(label='Data Titanic', value='tab-1', children =[
            html.Div([
                html.Div([
                    html.P('Survived : '),
                    dcc.Dropdown(
                        id='survivefilter',
                        options=[i for i in [{'label':'All', 'value':''},
                                            {'label':'Survived', 'value':'1'},
                                            {'label':'Not-Survived', 'value':'0'}]],
                        value=''
                    )
                ], className = 'col-3')
            ], className='row'),
            html.Div([
                html.Div([
                    html.P('Age : '),
                    dcc.RangeSlider(
                        id='agefilter',
                        min=dfTitanic['age'].min(),
                        max=dfTitanic['age'].max(),
                        value=[dfTitanic['age'].min(),dfTitanic['age'].max()],
                        marks={i : '{}'.format(i) for i in range(dfTitanic['age'].min(),dfTitanic['age'].max()+1,5)},
                        className='rangeslider'
                    )
                ], className = 'col-9'),
                html.Div([
                ], className = 'col-1'),
                html.Div([
                    html.Br(),
                    html.Button(
                        'Search',
                        id = 'buttonsearch',
                        style=dict(width='100%')
                    )
                ], className = 'col-2')
            ], className='row'),
            html.Br(),
            html.Br(),
            html.Div([
                html.Div([
                    html.P('Max Rows : '),
                    dcc.Input(
                        id='filterrow',
                        type='number',
                        value='10',
                        style=dict(width='50%')
                    )
                ], className = 'col-3')
            ], className = 'row'),
            html.Div([
                html.Center([
                    html.H2('Data Titanic', className='title'),
                    html.Div(
                        id='tabletitanic', children = generate_table(dfTitanic)
                    )
                ])
            ])
        ]),
        dcc.Tab(label='Categorical Plot', value='tab-2', children=[
            html.Div([
                html.Div([
                    html.P('Jenis Plot :'),
                    dcc.Dropdown(
                        id='jeniscatplot',
                        options=[{'label':i,'value':i} for i in ['Bar','Box','Violin']],
                        value='Bar'
                    )
                ], className = 'col-3'),
                html.Div([
                    html.P('X :'),
                    dcc.Dropdown(
                        id='xcatplot',
                        options=[{'label':i,'value':i} for i in ['sex','survived','embark_town','class','who','alone']],
                        value='sex'
                    )
                ], className = 'col-3'),
                html.Div([
                    html.P('Y :'),
                    dcc.Dropdown(
                        id='ycatplot',
                        options=[{'label':i,'value':i} for i in ['fare','age']],
                        value='fare'
                    )
                ], className = 'col-3'),
                html.Div([
                    html.P('Stats :'),
                    dcc.Dropdown(
                        id='statscatplot',
                        options=[i for i in [{'label':'Mean','value':'mean'},
                                            {'label':'Standart Deviation','value':'std'},
                                            {'label':'Count','value':'count'},
                                            {'label':'Min','value':'min'},
                                            {'label':'Max','value':'max'},
                                            {'label':'25th Precentiles','value':'25%'},
                                            {'label':'Median','value':'50%'},
                                            {'label':'75th Precentiles','value':'75%'}]],
                        value='mean'
                    )
                ], className = 'col-3'),
            ], className = 'row'),
            html.Br(),
            html.Br(),
            html.Br(),
            dcc.Graph(
                        id = 'catplotgraph',
                    )
        ]),
        ], style={
        'fontFamily':'system-ui'
    }, content_style={
        'fontFamily':'Arial',
        'borderBottom':'1px solid #d6d6d6',
        'borderLeft':'1px solid #d6d6d6',
        'borderRight':'1px solid #d6d6d6',
        'padding':'44px'
    }),
], style={
    'maxWidth':'1200px',
    'margin':'0 auto'
})

#_______________CALLBACK TAB 1_______________#

@app.callback(
    Output('table-multicol-sorting', "data"),
    [Input('table-multicol-sorting', "pagination_settings"),
     Input('table-multicol-sorting', "sorting_settings")])

def update_sort_paging_table(pagination_settings, sorting_settings):
    if len(sorting_settings):
        dff = dfTitanic.sort_values(
            [col['column_id'] for col in sorting_settings],
            ascending=[
                col['direction'] == 'asc'
                for col in sorting_settings
            ],
            inplace=False
        )
    else:
        # No sort is applied
        dff = dfTitanic

    return dff.iloc[
        pagination_settings['current_page']*pagination_settings['page_size']:
        (pagination_settings['current_page'] + 1)*pagination_settings['page_size']
    ].to_dict('rows')

@app.callback(
    Output(component_id='tabletitanic', component_property='children'),
    [Input('buttonsearch', 'n_clicks'),
    Input('filterrow', 'value')],
    [State('survivefilter', 'value'),
    State('agefilter', 'value')]
)
def update_table(button,row,survive,age):
    dfNew = dfTitanic[(dfTitanic['age'] >= age[0]) & (dfTitanic['age'] <= age[1])]
    if survive != '':
        dfNew = dfNew[dfNew['survived'] == int(survive)]
    return generate_table(dfNew, pagesize=row)

#_____________________________CALLBACK CATEGORICAL PLOT______________________________

funcDict = {'Bar':go.Bar,
            'Box':go.Box,
            'Violin':go.Violin}

def generateValue(legend,x,y,stats='mean'):
    return {
        'x' : {
            'Bar' : dfPokemon[dfPokemon['Legendary'] == legend][x].unique(),
            'Box' : dfPokemon[dfPokemon['Legendary'] == legend][x],
            'Violin' : dfPokemon[dfPokemon['Legendary'] == legend][x]
        },
        'y' : {
            'Bar' : dfPokemon[dfPokemon['Legendary'] == legend].groupby(x)[y].describe()[stats],
            'Box' : dfPokemon[dfPokemon['Legendary'] == legend][y],
            'Violin' : dfPokemon[dfPokemon['Legendary'] == legend][y]
        }
    }

@app.callback(Output('catplotgraph','figure'),
                [Input('jeniscatplot','value'),
                Input('xcatplot','value'),
                Input('ycatplot','value'),
                Input('statscatplot','value'),]
)

def update_catplot(jenis,x,y,stat):
    return dict(
        layout = go.Layout(
            title = '{} Plot Pokemon'.format(jenis),
            xaxis = dict(title = x),
            yaxis = dict(title = y),
            boxmode = 'group',
            violinmode = 'group'
        ),
        data = [
            funcDict[jenis](
                x = generateValue('True',x,y)['x'][jenis],
                y = generateValue('True',x,y,stat)['y'][jenis],
                name = 'Legendary'
            ),
            funcDict[jenis](
                x = generateValue('False',x,y)['x'][jenis],
                y = generateValue('False',x,y,stat)['y'][jenis],
                name = 'Non-Legendary'
            )
        ]
    )

@app.callback(Output('statscatplot','disabled'),
                [Input('jeniscatplot','value')]
)

def disabled_stats(jenis):
    if jenis != 'Bar':
        return True
    return False

if __name__ == '__main__':
    app.run_server(debug=True)