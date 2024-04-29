# Import required libraries
import numpy as np
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from style import CONTENT_STYLE
from sidebar import sidebar, dataframe_filter
from graphs import hot_topics, topic_bar_graph, engagement_statistics, posts, tf_idf

sm_df = pd.read_pickle('updated_testing_data.pkl')
weekly_df = pd.read_pickle('keywords.pkl')

# Topic Data Calculations
topics = list(set(val for sublist in sm_df['topics'] for val in sublist)) # Get the unique topics
column_sums = {} # Create a dictionary to store the topic sums
for topic in topics:
    keyword_sum = column_sums[topic] if topic in column_sums.keys() else 0
    for topic_list in sm_df['topics']:
        keyword_sum += topic_list.count(topic)
    column_sums[topic] = keyword_sum # Add a column for each topic to the dataframe
column_sums = pd.DataFrame(column_sums, index=[0]).T.reset_index() # Convert the dictionary to a dataframe
column_sums.rename(columns={'index': 'topic', 0: 'value'}, inplace=True) # Rename the columns
column_sums = column_sums.sort_values(['value'], ascending = False).head(20).reset_index()

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

maindiv_list = []
maindiv_list.append(tf_idf(weekly_df))
# maindiv_list.append(html.Br())
maindiv_list.append(engagement_statistics(sm_df))
# maindiv_list.append(hot_topics(column_sums))

maindiv = html.Div(
    id="first-div",
    children=[
        html.H1(id='title', children='Social Media Analytics Dashboard'),
        html.Div(
            children=[
                html.Hr(style={'borderTop': '2px solid black'}),
                html.H2(children='Time Period At a Glance', style={"textAlign":"left"}),
                html.Div(children=maindiv_list, 
                        style={"display": "inline-flex", "alignItems": "center", "gap": "2em"}),
                html.Div(children=[html.H4(id='New and Popular', children='See What\'s Popular', style={'fontStyle': 'italic', 'marginTop': '1em'}), 
                                   html.P('A collection of the most popular posts across platforms by the number of reactions, normalized by the number of followers of the author account.'),
                                   posts(sm_df)], style={"max-width": "100vw"}),
                html.Br(),
                html.Hr(style={'borderTop': '2px solid black'}),
                html.H2(children='Content and Engagement', style={"textAlign":"left"})
            ]
        )
    ],
    style = CONTENT_STYLE
)

app.layout = html.Div([sidebar, maindiv])

# Account Categories - option handling
@app.callback(
    Output("account-category", "value"),
    [Input("all-or-none-category", "value")],
    [State("account-category", "options")],
)
def select_all_none_category(all_selected, options):
    all_or_none = []
    all_or_none = [option["value"] for option in options if all_selected]
    return all_or_none

# COM-B option handling
@app.callback(
    Output("com-b-components", "value"),
    [Input("all-or-none-com-b", "value")],
    [State("com-b-components", "options")],
)
def select_all_none_category(all_selected, options):
    all_or_none = []
    all_or_none = [option["value"] for option in options if all_selected]
    return all_or_none

# Callback for dates
@app.callback(
    [Output(component_id='date-range-div', component_property='style'),
     Output(component_id='relative-date-div', component_property='style')],
    [Input(component_id='time-frame', component_property='value')]
)
def date_options(visibility_state):
    show = {'display': 'block'}
    hide = {'display': 'none'}
    
    if visibility_state == "relative":
        return hide, show
    else:
        return show, hide

# Graph + Chart Callback Functions
@app.callback(
        # Output("topic-bar-graph", "figure"),
        Output("engagement", "children"),
        Output("posts", "children"),
        Output("tf-idf", "children"),
    
        # Platform Selection
        Input("platform-selection", "value"),
         
        # Account categories
        Input("account-category", "value"),

        # Account identity
        Input("account-identity", "value"),

        # Account type
        Input("account-type", "value"),

        # Account location
        Input("account-location", "value"),

        # Time frame values
        Input("time-frame", "value"),
        Input("dates-dropdown", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date")

        # Input("com-b-components", "value") - COM-B components for later implementation
    )

def graphs(platform_list, account_category, account_identity, account_type, account_location, time_frame, relative_date, start_date, end_date):
    # Filter the dataframe based on the selected platforms and the selected labels
    result = dataframe_filter(sm_df, weekly_df, platform_list, account_category, account_identity, account_type, account_location, time_frame, relative_date, start_date, end_date)
    filtered_df = result[0]
    start_date = result[1] # Save the start and end dates for x-axis labels
    end_date = result[2]

    topic_df = filtered_df
    topics = list(set(val for sublist in topic_df['topics'] for val in sublist)) # Get the unique topics

    filtered_df = filtered_df.groupby(['authoredAt', 'platform']).agg({'positive': 'mean', 'negative': 'mean', 'compound': 'mean'}).reset_index()
    filtered_df['compound_7day'] = filtered_df['compound'].rolling(window=7).mean()

    # Topic Bar Graph
    column_sums = {}
    for topic in topics:
        keyword_sum = column_sums[topic] if topic in column_sums.keys() else 0
        for topic_list in topic_df['topics']:
            keyword_sum += topic_list.count(topic)
        column_sums[topic] = keyword_sum # Add a column for each topic to the dataframe
    column_sums = pd.DataFrame(column_sums, index=[0]).T.reset_index() # Convert the dictionary to a dataframe
    column_sums.rename(columns={'index': 'topic', 0: 'value'}, inplace=True) # Rename the columns
    column_sums = column_sums.sort_values(['value'], ascending = False).head(20).reset_index()

    return engagement_statistics(result[0]), posts(result[0]), tf_idf(result[1]) #, topic_bar_graph(column_sums),