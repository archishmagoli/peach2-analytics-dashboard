# Import required libraries
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

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
labels = sm_df.iloc[:, 23:].columns.tolist()

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "20rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
    "overflow": "scroll"
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "22rem",
    "width": "calc(100% - 22rem)",
    "text-align": "center",
    "padding": "2rem 1rem",
    "display": "inline-block"
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
            dcc.Dropdown(['Last 15 Days', 'Last 30 Days', 'Last 60 Days',
                            'Last 90 Days', 'Last 6 Months', 'Last 1 Year', 'All Dates'], 'All Dates', id='dates-dropdown'),
        ]),  # Adjust the width as needed
        
        html.Br(),
        # Filter By Labels
        html.Div([
            html.H4('Filter By Post Labels'),
            html.H5('Account Categories'),
            dcc.RadioItems(
                id="account-category",
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
        ]),  # Adjust the width as needed
    ],
    style=SIDEBAR_STYLE,
)

maindiv = html.Div(
    id="first-div",
    children=[
        html.H1('Social Media Analytics Dashboard'),
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
    ],
    style=CONTENT_STYLE
)

app.layout = html.Div([sidebar, maindiv])

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
if __name__ == "__main__":
    app.run_server(port=8000)