# Import required libraries
import numpy as np
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Load the dataframe
sm_df = pd.read_pickle('sentiment_data_vader_labels.pkl')

# authoredAt column manipulation for timeseries grouping
sm_df['authoredAt'] = pd.to_datetime(sm_df['authoredAt'])
sm_df['authoredAt'] = sm_df['authoredAt'].dt.date
sentiment_means = sm_df.groupby(['authoredAt', 'platform']).agg({'positive': 'mean', 'negative': 'mean', 'compound': 'mean'}).reset_index()
sentiment_means['positive_7day'] = sentiment_means['positive'].rolling(window=7).mean()
sentiment_means['negative_7day'] = sentiment_means['negative'].rolling(window=7).mean()
sentiment_means['compound_7day'] = sentiment_means['compound'].rolling(window=7).mean()
post_count = (sm_df['authoredAt'].value_counts().sort_index().rolling(window=7).mean()).values
np.nan_to_num(post_count, nan=0, copy=False)
posts_counts = pd.DataFrame({'authoredAt': sm_df['authoredAt'].unique(), 'post_count': post_count})
yaxis_range=[0, post_count.max() + 100 if len(post_count) > 0 else 1200] # Get absolute maximum y-axis value for consistency
sm_df['sentiment'] = sm_df['compound'].apply(lambda x: 'positive' if x >= 0.1 else ('negative' if x <= -0.1 else 'neutral'))
sentiment_count = sm_df.groupby(['sentiment'])['sentiment'].count().reset_index(name='count')
labels = sm_df.iloc[:, 23:].columns.tolist()

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "22rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
    "overflow": "auto",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "24rem",
    "width": "calc(100% - 24rem)",
    "text-align": "center",
    "padding": "2rem 1rem",
    "display": "inline-block",
}

sidebar = html.Div(
    [# Filter By Social Media Platform and Time Frame
        html.Div([
            html.H4('Filter By Platform'),
            dcc.Checklist(id='platform-selection',
                        options=[{'label': platform.capitalize(), 'value': platform} for platform in sm_df.platform.unique()],
                        value=sm_df.platform.unique(),
                        inputStyle={"margin-right":"0.5rem", "margin-left":"0.5rem"}),
            html.Br(),
            html.H4('Filter By Time Frame'),
            dcc.RadioItems(
                id="time-frame",
                options=[
                    {"label": "Use Relative Dates", "value": "relative"},
                    {"label": "Select Custom Range", "value": "range"},
                ],
                value="relative",
                inputStyle={"margin-right":"0.5rem", "margin-left":"0.5rem"}
            ),
            html.Div(id='date-range-div', children=[
                html.Br(),
                dcc.DatePickerRange(
                    start_date_placeholder_text="Start Date",
                    end_date_placeholder_text="End Date",
                    calendar_orientation='vertical',
                    id='date-range',
                    min_date_allowed=sm_df['authoredAt'].min(),
                    max_date_allowed=sm_df['authoredAt'].max(),
                    initial_visible_month=sm_df['authoredAt'].max(),
                    start_date=sm_df['authoredAt'].min(),
                    end_date=sm_df['authoredAt'].max(),
                    display_format='MM/DD/YYYY',
                ),
            ], style={'display': 'none', }, className="dbc"),

            html.Div(id='relative-date-div', children=[
                html.Br(),
                dcc.Dropdown(['Last 15 Days', 'Last 30 Days', 'Last 60 Days',
                            'Last 90 Days', 'Last 6 Months', 'Last 1 Year', 'All Dates'], 'All Dates', id='dates-dropdown'),
            ], style={'display': 'block'}),
        ]),
        
        html.Br(),
        # Filter By Labels
        html.Div([
            html.H4('Filter By Post Labels'),
            html.H5('Account Categories'),
            dcc.Checklist(
                id="all-or-none-category",
                options=[{"label": "All", "value": "all"}],
                value=[],
                inputStyle={"margin-right":"0.5rem", "margin-left":"0.5rem"}
            ),
            dcc.Checklist(
                id="account-category",
                options=[
                    {"label": "Government", "value": "government"},
                    {"label": "Media", "value": "media"},
                    {"label": "Faith", "value": "faith"},
                    {"label": "Health", "value": "health"},
                    {"label": "Diabetes", "value": "diabetes"},
                    {"label": "Known Misinfo Spreaders", "value": "misinfo"},
                    {"label": "Project Partners", "value": "partners"},
                    {"label": "Trusted Resources", "value": "trusted"},
                ],
                value=[],
                inputStyle={"margin-right":"0.5rem", "margin-left":"0.5rem"}
            ),
            html.Br(),
            html.H5('Account Identity'),
            dcc.RadioItems(
                id="account-identity",
                options=[
                    {"label": "All", "value": "all"},
                    {"label": "Black/African American", "value": "blackafam"},
                    {"label": "Hispanic/Latinx", "value": "latinx"},
                ],
                value="all",
                inputStyle={"margin-right":"0.5rem", "margin-left":"0.5rem"}
            ),
            html.Br(),
            html.H5('Account Type'),
            dcc.RadioItems(
                id="account-type",
                options=[
                    {"label": "All", "value": "all"},
                    {"label": "Institution", "value": "institutional"},
                    {"label": "Non-Institution", "value": "non-institutional"},
                ],
                value="all",
                inputStyle={"margin-right":"0.5rem", "margin-left":"0.5rem"}
            ),
            html.Br(),
            html.H5('Account Location'),
            dcc.RadioItems(
                id="account-location",
                options=[
                    {"label": "All", "value": "all"},
                    {"label": "Georgia", "value": "georgia"},
                    {"label": "Non-Georgia", "value": "non-georgia"},
                ],
                value="all",
                inputStyle={"margin-right":"0.5rem", "margin-left":"0.5rem"}
            ),
            html.Br(),
            html.Div([
            html.H5('COM-B Components'),
            dcc.Checklist(
                id="all-or-none-com-b",
                options=[{"label": "All", "value": "all"}],
                value=[],
                inputStyle={"margin-right":"0.5rem", "margin-left":"0.5rem"}
            ),
            dcc.Checklist(
                id="com-b-components",
                options=[
                    {"label": "Physical Capability", "value": "physical-capability"},
                    {"label": "Psychological Capability", "value": "psychological-capability"},
                    {"label": "Reflective Motivation", "value": "reflective-motivation"},
                    {"label": "Automatic Motivation", "value": "automatic-motivation"},
                    {"label": "Physical Opportunity", "value": "physical-opportunity"},
                    {"label": "Social Opportunity", "value": "social-opportunity"},
                ],
                value=[],
                inputStyle={"margin-right":"0.5rem", "margin-left":"0.5rem"}
            ),
            html.Br(),
            ]),  # Adjust the width as needed
        ]),
    ],
    
    style=SIDEBAR_STYLE,
)

maindiv = html.Div(
    id="first-div",
    children=[
       html.H1('Social Media Analytics Dashboard'),
       html.Div([
           dcc.Graph(id='compound-sentiment-line-graph', 
                    figure = px.line(sentiment_means, x=sentiment_means['authoredAt'], y=['compound_7day'], labels={'compound_7day':'Average Compound Sentiment'}))]),
        html.Br(),

        html.Div(dcc.Graph(id='posts-line-graph', 
                    figure = px.line(posts_counts, x=posts_counts['authoredAt'], y=posts_counts['post_count'],
                    title='Average Number of Posts Over Time', labels={'authoredAt':'Date', 'value':'Posts Count'}))),
        html.Br(),

        # html.Div(dcc.Graph(
        #             id='sentiment-pie-chart',
        #             figure=px.pie(
        #                 sentiment_count,
        #                 names='sentiment',
        #                 values='count',
        #                 title='Post Sentiment Breakdown',
        #                 color_discrete_sequence=px.colors.sequential.RdBu,
        #                 labels={'sentiment': 'Sentiment', 'count': 'Count'}
        #             ),
        #             style={'border': '2px solid #e8e8e8', 'background-color': '#f8f9fa'}
        #         )),
        # html.Br(),
    ],
    style=CONTENT_STYLE
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
    

# # Add a callback function for `platform-selection` as input, `sentiment-pie-chart` as output
# @app.callback(
#         [Output("sentiment-pie-chart", "figure")],

#         [Input("platform-selection", "value"),
         
#          # Account categories
#          Input("all-or-none-category", "value"),
#          Input("account-category", "value"),

#          # Account identity
#          Input("account-identity", "value"),

#          # Account type
#          Input("account-type", "value"),

#          # Account location
#          Input("account-location", "value"),

#          # Time frame values
#          Input("time-frame", "value"),
#          Input("relative-date-div", "value"),
#          Input("date-range", "start_date"),
#          Input("date-range", "end_date")

#          # Input("com-b-components", "value") - COM-B components for later implementation
#          ])
# def get_pie_chart(platform_list, select_all_none_category, account_category, account_identity, account_type, account_location, time_frame, relative_date, start_date, end_date):
#     filtered_df = dataframe_filter(sm_df, platform_list, select_all_none_category, account_category, account_identity, account_type, account_location, time_frame, relative_date, start_date, end_date)

#     sentiment_count = filtered_df.groupby(['sentiment'])['sentiment'].count().reset_index(name='count')
#     figure = px.pie(
#         sentiment_count,
#         names='sentiment',
#         values='count',
#         title='Post Sentiment Breakdown',
#         color_discrete_sequence=px.colors.sequential.RdBu)
    
#     figure.update_layout(
#         title={'text': 'Post Sentiment Breakdown', 'x': 0.5, 'font': {'size': 20, 'color': 'black'}, 'y': 0.9},
#         legend={'title': 'Sentiment', 'font': {'size': 14, 'color': 'black'}}
#     )
    
#     return figure

# Compounnd Sentiment Line Graph - Callback Function
@app.callback(
        Output("compound-sentiment-line-graph", "figure"),
        Output("posts-line-graph", "figure"),
    
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
def line_graphs(platform_list, account_category, account_identity, account_type, account_location, time_frame, relative_date, start_date, end_date):
    # Filter the dataframe based on the selected platforms and the selected labels
    result = dataframe_filter(sm_df, platform_list, account_category, account_identity, account_type, account_location, time_frame, relative_date, start_date, end_date)
    filtered_df = result[0]
    start_date = result[1] # Save the start and end dates for x-axis labels
    end_date = result[2]

    post_count = (filtered_df['authoredAt'].value_counts().sort_index().rolling(window=7).mean()).values
    filtered_df = filtered_df.groupby(['authoredAt', 'platform']).agg({'positive': 'mean', 'negative': 'mean', 'compound': 'mean'}).reset_index()
    filtered_df['compound_7day'] = filtered_df['compound'].rolling(window=7).mean()
    
    # Compound Sentiment Line Graph
    compound_sentiment_line_graph = go.Figure() # Create a figure with dual y-axes
    compound_sentiment_line_graph.add_trace(go.Scatter(x=filtered_df['authoredAt'], y=filtered_df['compound_7day'], mode='lines', name='Compound (7-day)', line=dict(color='blue', width=2))) # Add the compound sentiment line with adjusted style
    compound_sentiment_line_graph.add_hline(y=0)
    compound_sentiment_line_graph.update_layout( # Update the layout of the figure
        xaxis_title='Date',
        yaxis_title='Sentiment',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font_family='Open Sans',
        font_color='black',
        title_x=0.5,
        xaxis_range=[start_date, end_date],
        yaxis_range=[-1, 1],
        legend_title="Sentiment Lines",
        showlegend=True
    )

    # Posts Line Graph
    np.nan_to_num(post_count, nan=0, copy=False)
    posts_counts = pd.DataFrame({'authoredAt': filtered_df['authoredAt'].unique(), 'post_count': post_count})

    posts_line_graph = go.Figure() # Create a figure with dual y-axes
    posts_line_graph.add_hline(y=0)
    posts_line_graph.add_trace(go.Scatter(x=posts_counts['authoredAt'], y=posts_counts['post_count'], mode='lines', name='Posts (7-day)', line=dict(color='purple', width=2))) # Add the compound sentiment line with adjusted style
    posts_line_graph.update_layout( # Update the layout of the figure
        title = 'Average Number of Posts Over Time',
        xaxis_title = 'Date',
        yaxis_title = 'Posts Count',
        legend_title_text = 'Posts',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font_family='Open Sans',
        font_color='black',
        title_x=0.5,
        xaxis_range=[start_date, end_date],
        yaxis_range=yaxis_range,
        legend_title="Posts"
    )

    return compound_sentiment_line_graph, posts_line_graph
    

def dataframe_filter(sm_df, platform_list, account_category, account_identity, account_type, account_location, time_frame, relative_date, start_date, end_date):
    ## Filter the dataframe based on the selected platforms and the selected labels
    filtered_df = sm_df[sm_df['platform'].isin(platform_list)]

    # Account Category
    for account in account_category:
        filtered_df = filtered_df[filtered_df[account] == 1]
    
    # Account Identity
    if account_identity != 'all':
        filtered_df = filtered_df[filtered_df[account_identity] == 1]
    
    # Account Type
    if account_type != 'all':
        if account_type == 'institutional':
            filtered_df = filtered_df[filtered_df['institutional'] == 1]
        else:
            filtered_df = filtered_df[filtered_df['institutional'] == 0]

    # Acccount Location
    if account_location != 'all':
        if account_location == 'georgia':
            filtered_df = filtered_df[filtered_df['georgia'] == 1]
        else:
            filtered_df = filtered_df[filtered_df['georgia'] == 0]

    # Relative vs. Custom Date Range
    if time_frame == 'relative':
        current_date = datetime.now()
        start_date = None

        if relative_date != 'All Dates':
            if relative_date == 'Last 15 Days':
                start_date = current_date - pd.DateOffset(days=15)
                start_date = start_date.date()
            elif relative_date == 'Last 30 Days':
                start_date = current_date - pd.DateOffset(days=30)
                start_date = start_date.date()
            elif relative_date == 'Last 60 Days':
                start_date = current_date - pd.DateOffset(days=60)
                start_date = start_date.date()
            elif relative_date == 'Last 90 Days':
                start_date = current_date - pd.DateOffset(days=90)
                start_date = start_date.date()
            elif relative_date == 'Last 6 Months':
                start_date = current_date - pd.DateOffset(months=6)
                start_date = start_date.date()
            elif relative_date == 'Last 1 Year':
                start_date = current_date - pd.DateOffset(years=1)
                start_date = start_date.date()
            filtered_df = filtered_df[filtered_df['authoredAt'] >= start_date]

    else:
        filtered_df = filtered_df[(filtered_df['authoredAt'] >= start_date) & (filtered_df['authoredAt'] <= end_date)]

    return [filtered_df, start_date, end_date]