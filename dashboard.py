# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
# Load the dataframe
sm_df = pd.read_csv('sentiment_data_vader_labels.csv')

# authoredAt column manipulation for timeseries grouping
sm_df['authoredAt'] = pd.to_datetime(sm_df['authoredAt'])
sm_df['authoredAt'] = sm_df['authoredAt'].dt.date
sentiment_means = sm_df.groupby(['authoredAt', 'platform']).agg({'positive': 'mean', 'negative': 'mean', 'compound': 'mean'}).reset_index()
sentiment_means['positive_7day'] = sentiment_means['positive'].rolling(window=7).mean()
sentiment_means['negative_7day'] = sentiment_means['negative'].rolling(window=7).mean()
sentiment_means['compound_7day'] = sentiment_means['compound'].rolling(window=7).mean()
post_count = (sm_df['authoredAt'].value_counts().sort_index().rolling(window=7).mean()).values
labels = sm_df.iloc[:, 23:].columns.tolist()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('Social Media Analysis Dashboard',
                                        style={'textAlign': 'center', 'color': '#000000',
                                               'font-size': 40, 'font-family': 'Open Sans'}),
                                # Add checkbox list for selecting social media platforms
                                # The default values will be that *all* platforms are selected
                                html.Div([
                                    # Filter By Social Media Platform
                                    html.Div([
                                        html.H3('Filter By Social Media Platform',
                                                style={'color': '#000000','font-size': 25, 'font-family': 'Open Sans', 'text-align': 'center'}),
                                    
                                        dcc.Checklist(id='platform-selection',
                                                    options=[{'label': platform.capitalize(), 'value': platform} for platform in sm_df.platform.unique()],
                                                    value=sm_df.platform.unique(),
                                                    labelStyle={'font-size': 15, 'font-family': 'Open Sans', 'padding-left': '10em'}),
                                    
                                        html.Br(),
                                        html.H3('Filter By a Specific Time Frame',
                                                style={'color': '#000000',
                                                    'font-size': 25, 'font-family': 'Open Sans', 'text-align': 'center'}),
                                        dcc.Dropdown(['Last 15 Days', 'Last 30 Days', 'Last 60 Days',
                                                      'Last 90 Days', 'Last 6 Months', 'Last 1 Year', 'All Dates'], 'All Dates', id='dates-dropdown',
                                                    style={'font-size': 15, 'font-family': 'Open Sans', 'padding-left': '10em'}),
                                    ], style={'display': 'inline-block', 'width': '48%', 'vertical-align': 'top'}),  # Adjust the width as needed
                                    
                                    # Filter By Labels
                                    html.Div([
                                        html.H3('Filter By Post Labels',
                                                style={'textAlign': 'left', 'color': '#000000',
                                                    'font-size': 25, 'font-family': 'Open Sans', 'text-align': 'center'}),
                                        html.H4('Account Categories',
                                                style={'textAlign': 'left', 'color': '#000000', 'font-size': 20, 'font-family': 'Open Sans', 'text-align': 'center'}),
                                        dcc.RadioItems(
                                            id="account-category",
                                            labelStyle={'font-size': 15, 'font-family': 'Open Sans', 'padding-left': '15em'},
                                            options=[
                                                {"label": "All", "value": "all"},
                                                {"label": "Government", "value": "government"},
                                                {"label": "Media", "value": "media"},
                                                {"label": "Faith", "value": "faith"},
                                                {"label": "Health", "value": "health"},
                                                {"label": "Diabetes", "value": "diabetes"},
                                                {"label": "Known Misinfo Spreaders", "value": "misinfo"},
                                                {"label": "Project Partners", "value": "partners"},
                                                {"label": "Trusted Resources", "value": "trusted"},
                                            ],
                                            value="all",
                                        ),

                                        html.H4('Account Identity',
                                                style={'textAlign': 'left', 'color': '#000000', 'font-size': 20, 'font-family': 'Open Sans', 'text-align': 'center'}),
                                        dcc.RadioItems(
                                            id="account-identity",
                                            labelStyle={'font-size': 15, 'font-family': 'Open Sans', 'padding-left': '15em'},
                                            options=[
                                                {"label": "All", "value": "all"},
                                                {"label": "Black/African American", "value": "blackafam"},
                                                {"label": "Hispanic/Latinx", "value": "latinx"},
                                            ],
                                            value="all",
                                        ),

                                        html.H4('Account Type',
                                                style={'textAlign': 'left', 'color': '#000000', 'font-size': 20, 'font-family': 'Open Sans', 'text-align': 'center'}),
                                        dcc.RadioItems(
                                            id="account-type",
                                            labelStyle={'font-size': 15, 'font-family': 'Open Sans', 'padding-left': '15em'},
                                            options=[
                                                {"label": "All", "value": "all"},
                                                {"label": "Institution", "value": "institutional"},
                                                {"label": "Non-Institution", "value": "non-institutional"},
                                            ],
                                            value="all",
                                        ),

                                        html.H4('Account Location',
                                                style={'textAlign': 'left', 'color': '#000000', 'font-size': 20, 'font-family': 'Open Sans', 'text-align': 'center'}),
                                        dcc.RadioItems(
                                            id="account-location",
                                            labelStyle={'font-size': 15, 'font-family': 'Open Sans', 'padding-left': '15em'},
                                            options=[
                                                {"label": "All", "value": "all"},
                                                {"label": "Georgia", "value": "georgia"},
                                                {"label": "Non-Georgia", "value": "non-georgia"},
                                            ],
                                            value="all",
                                        ),
                                    ], style={'display': 'inline-block', 'width': '48%', 'vertical-align': 'top'}),  # Adjust the width as needed
                                ]),
                                # Show the average sentiment over time through a line graph
                                # If a specific platform was selected, show the average sentiment only for the selected platform
                                # TODO: Create a time filter (i.e. a range slider) for the line graph
                                html.Div(dcc.Graph(id='compound-sentiment-line-graph', 
                                                    figure = px.line(sentiment_means, x=sentiment_means['authoredAt'], y=['compound_7day'],
                                                    title='Average Compound Sentiment Over Time', labels={'authoredAt':'Date', 'value':'Average Sentiment'}))),
                                html.Br(),
                                html.Div(dcc.Graph(id='emotion-sentiment-line-graph', 
                                                    figure = px.line(sentiment_means, x=sentiment_means['authoredAt'], y=['positive_7day', 'negative_7day'],
                                                    title='Average Sentiment Over Time', labels={'authoredAt':'Date', 'value':'Average Sentiment'}))),
                                html.Br(),
                                html.Div(dcc.Graph(id='posts-line-graph', 
                                                    figure = px.line(sentiment_means, x=sentiment_means['authoredAt'].unique(), y=post_count,
                                                    title='Average Number of Posts Over Time', labels={'authoredAt':'Date', 'value':'Posts Count'}))),
                    ])

# Add a callback function for `platform-selection` as input, `compound-sentiment-line-graph` as output
@app.callback(Output("compound-sentiment-line-graph", "figure"), Input("platform-selection", "value"), Input("account-category", "value"), Input("account-identity", "value"), Input("account-type", "value"), Input("account-location", "value"), Input("dates-dropdown", "value"))
def get_line_chart(platform_list, account_category, account_identity, account_type, account_location, date_range):
    filtered_df = dataframe_filter(platform_list, sm_df, account_category, account_identity, account_type, account_location, date_range)

    filtered_df = filtered_df.groupby(['authoredAt', 'platform']).agg({'positive': 'mean', 'negative': 'mean', 'compound': 'mean'}).reset_index()
    filtered_df['compound_7day'] = filtered_df['compound'].rolling(window=7).mean()
    
    # Create a figure with dual y-axes
    figure = go.Figure()

    # Add the compound sentiment line with adjusted style
    figure.add_trace(go.Scatter(x=filtered_df['authoredAt'], y=filtered_df['compound_7day'], mode='lines', name='Compound (7-day)', line=dict(color='blue', width=2)))

    figure.add_hline(y=0)
    
    # Update the layout of the figure
    figure.update_layout(
        title='Average Compound Sentiment Over Time',
        xaxis_title='Date',
        yaxis_title='Sentiment',
        legend_title_text='Sentiment',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font_family='Open Sans',
        font_color='black',
        title_x=0.5,
    )

    return figure

# Add a callback function for `platform-selection` as input, `posts-line-graph` as output
@app.callback(Output("posts-line-graph", "figure"), Input("platform-selection", "value"), Input("account-category", "value"), Input("account-identity", "value"), Input("account-type", "value"), Input("account-location", "value"), Input("dates-dropdown", "value"))
def get_line_chart(platform_list, account_category, account_identity, account_type, account_location, date_range):
    # Filter the dataframe based on the selected platforms and the selected labels
    filtered_df = dataframe_filter(platform_list, sm_df, account_category, account_identity, account_type, account_location, date_range)

    filtered_post_count = filtered_df['authoredAt'].value_counts().sort_index().rolling(window=7).mean()
    filtered_post_count = filtered_post_count.sort_index()
    filtered_post_count = filtered_post_count.dropna()
    filtered_post_count = filtered_post_count.values
    
    # Create a figure with dual y-axes
    figure = go.Figure()

    # Add the positive sentiment line with adjusted style
    figure.add_trace(go.Scatter(x=sorted(filtered_df['authoredAt'].unique()), y=filtered_post_count, mode='lines', name='Post Average (7-day)', line=dict(color='purple', width=2)))

    figure.add_hline(y=0)

    # Update the layout of the figure
    figure.update_layout(
        title='Average Number of Posts Over Time',
        xaxis_title='Date',
        yaxis_title='Post Count',
        legend_title_text='Post Count',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font_family='Open Sans',
        font_color='black',
        title_x=0.5,
    )

    return figure

# Add a callback function for `platform-selection` as input, `emotion-sentiment-line-graph` as output
@app.callback(Output("emotion-sentiment-line-graph", "figure"), Input("platform-selection", "value"), Input("account-category", "value"), Input("account-identity", "value"), Input("account-type", "value"), Input("account-location", "value"), Input("dates-dropdown", "value"))
def get_line_chart(platform_list, account_category, account_identity, account_type, account_location, date_range):

    # Filter the dataframe based on the selected platforms and the selected labels
    filtered_df = dataframe_filter(platform_list, sm_df, account_category, account_identity, account_type, account_location, date_range)

    filtered_df = filtered_df.groupby(['authoredAt', 'platform']).agg({'positive': 'mean', 'negative': 'mean', 'compound': 'mean'}).reset_index()
    filtered_df['positive_7day'] = filtered_df['positive'].rolling(window=7).mean()
    filtered_df['negative_7day'] = filtered_df['negative'].rolling(window=7).mean()
    
    # Create a figure with dual y-axes
    figure = go.Figure()

    # Add the positive sentiment line with adjusted style
    figure.add_trace(go.Scatter(x=filtered_df['authoredAt'], y=filtered_df['positive_7day'], mode='lines', name='Positive (7-day)', line=dict(color='red', width=2)))
    figure.add_trace(go.Scatter(x=filtered_df['authoredAt'], y=filtered_df['negative_7day'], mode='lines', name='Negative (7-day)', line=dict(color='green', width=2)))

    figure.add_hline(y=0)
    
    # Update the layout of the figure
    figure.update_layout(
        title='Average Positive and Negative Sentiment Over Time',
        xaxis_title='Date',
        yaxis_title='Sentiment',
        legend_title_text='Sentiment',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font_family='Open Sans',
        font_color='black',
        title_x=0.5,
    )

    return figure


def dataframe_filter(platform_list, sm_df, account_category, account_identity, account_type, account_location, date_range):
    # Filter the dataframe based on the selected platforms and the selected labels
    filtered_df = sm_df[sm_df['platform'].isin(platform_list)]

    if account_category != 'all':
        filtered_df = filtered_df[filtered_df[account_category] == 1]
    
    if account_identity != 'all':
        filtered_df = filtered_df[filtered_df[account_identity] == 1]
    
    if account_type != 'all':
        if account_type == 'institutional':
            filtered_df = filtered_df[filtered_df['institutional'] == 1]
        else:
            filtered_df = filtered_df[filtered_df['institutional'] == 0]

    if account_location != 'all':
        if account_location == 'georgia':
            filtered_df = filtered_df[filtered_df['georgia'] == 1]
        else:
            filtered_df = filtered_df[filtered_df['georgia'] == 0]

    if date_range != 'All Dates':
        current_date = datetime.now()
        start_date = None

        if date_range == 'Last 15 Days':
            start_date = pd.to_datetime(current_date) - timedelta(days=15)
            start_date = start_date.date()
        elif date_range == 'Last 30 Days':
            start_date = current_date - pd.DateOffset(days=30)
            start_date = start_date.date()
        elif date_range == 'Last 60 Days':
            start_date = current_date - pd.DateOffset(days=60)
            start_date = start_date.date()
        elif date_range == 'Last 90 Days':
            start_date = current_date - pd.DateOffset(days=90)
            start_date = start_date.date()
        elif date_range == 'Last 6 Months':
            start_date = current_date - pd.DateOffset(months=6)
            start_date = start_date.date()
        elif date_range == 'Last 1 Year':
            start_date = current_date - pd.DateOffset(years=1)
            start_date = start_date.date()

        filtered_df = filtered_df[filtered_df['authoredAt'] >= start_date]

    return filtered_df

# Run the app
if __name__ == '__main__':
    app.run_server()