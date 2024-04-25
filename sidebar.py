# Import required libraries
from dash import html, dcc
from style import SIDEBAR_STYLE
from datetime import datetime
import pandas as pd

sm_df = pd.read_pickle('testing_data_vader.pkl')

sidebar = html.Div(
    [# Filter By Social Media Platform and Time Frame
        html.Div([
            html.H4('Filter By Platform'),
            dcc.Checklist(id='platform-selection',
                        options=[{'label': platform.capitalize(), 'value': platform} for platform in sm_df.platform.unique()],
                        value=sm_df.platform.unique(),
                        inputStyle={"marginRight":"0.5rem", "marginLeft":"0.5rem"}),
            html.Br(),
            html.H4('Filter By Time Frame'),
            dcc.RadioItems(
                id="time-frame",
                options=[
                    {"label": "Use Relative Dates", "value": "relative"},
                    {"label": "Select Custom Range", "value": "range"},
                ],
                value="relative",
                inputStyle={"marginRight":"0.5rem", "marginLeft":"0.5rem"}
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
                dcc.Dropdown(['Last 7 Days', 'Last 15 Days', 'Last 30 Days', 'Last 60 Days',
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
                inputStyle={"marginRight":"0.5rem", "marginLeft":"0.5rem"}
            ),
            dcc.Checklist(
                id="account-category",
                options=[
                    {"label": "Government", "value": "government"},
                    {"label": "Media", "value": "media"},
                    {"label": "Faith", "value": "faith"},
                    {"label": "Health", "value": "health"},
                    {"label": "COVID", "value": "covid"},
                    {"label": "Known Misinfo Spreaders", "value": "misinfo"},
                    {"label": "Project Partners", "value": "partners"},
                    {"label": "Trusted Resources", "value": "trusted"}
                ],
                value=[],
                inputStyle={"marginRight":"0.5rem", "marginLeft":"0.5rem"}
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
                inputStyle={"marginRight":"0.5rem", "marginLeft":"0.5rem"}
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
                inputStyle={"marginRight":"0.5rem", "marginLeft":"0.5rem"}
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
                inputStyle={"marginRight":"0.5rem", "marginLeft":"0.5rem"}
            ),
            html.Br(),
            html.Div([
            html.H5('COM-B Components'),
            dcc.Checklist(
                id="all-or-none-com-b",
                options=[{"label": "All", "value": "all"}],
                value=[],
                inputStyle={"marginRight":"0.5rem", "marginLeft":"0.5rem"}
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
                inputStyle={"marginRight":"0.5rem", "marginLeft":"0.5rem"}
            ),
            html.Br(),
            ]),  # Adjust the width as needed
        ]),
    ],
    style=SIDEBAR_STYLE,
)

def dataframe_filter(sm_df, weekly_df, platform_list, account_category, account_identity, account_type, account_location, time_frame, relative_date, start_date, end_date):
    ## Filter the dataframe based on the selected platforms and the selected labels
    filtered_df = sm_df[sm_df['platform'].isin(platform_list)]
    filtered_weekly_df = weekly_df

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
        current_date = filtered_df['authoredAt'].max()
        start_date = None

        if relative_date != 'All Dates':
            end_date = current_date.date()
            if relative_date == 'Last 7 Days':
                start_date = current_date - pd.DateOffset(days=7)
                start_date = start_date.date()
            elif relative_date == 'Last 15 Days':
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
            filtered_df = filtered_df[filtered_df['authoredAt'] >= datetime.combine(start_date, datetime.min.time())]
            filtered_weekly_df = filtered_weekly_df[filtered_weekly_df['weekAuthored'] >= datetime.combine(start_date, datetime.min.time())]

    else:
        date_format = '%Y-%m-%d'
        start_date = datetime.strptime(start_date, date_format).date() if isinstance(start_date, str) else start_date
        end_date = datetime.strptime(end_date, date_format).date() if isinstance(end_date, str) else end_date
        filtered_df = filtered_df[(filtered_df['authoredAt'] >=  datetime.combine(start_date, datetime.min.time())) & (filtered_df['authoredAt'].date() <= datetime.combine(end_date, datetime.min.time()))]
        filtered_weekly_df = filtered_weekly_df[(filtered_weekly_df['weekAuthored'] >=  datetime.combine(start_date, datetime.min.time())) & (filtered_weekly_df['weekAuthored'].date() <= datetime.combine(end_date, datetime.min.time()))]

    return [filtered_df, filtered_weekly_df, start_date, end_date]