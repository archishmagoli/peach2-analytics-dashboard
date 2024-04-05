# Import required libraries
import numpy as np
import ast
from datetime import datetime
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_process import process_pickle

sm_df = process_pickle()

def hot_topics(column_sums):
    return html.Div(id='hot_topics',
            children=[
                html.H4(id='Hot Topics', children='Hot Topics 🔥', style={'fontStyle': 'italic'}),
                dcc.Graph(
                    id='topic-bar-graph',
                    figure = px.bar(
                        column_sums, 
                        x=column_sums['topic'],
                        y=column_sums['value'],
                        title='Topic Breakdown of Social Media Posts',
                        color_discrete_sequence=px.colors.qualitative.Prism),
                    style = {'border': '1px solid black', 'min-width': '30rem'}
                ),
            ],
            style={'textAlign': 'left', 'width': '75%'}
        )

def topic_bar_graph(column_sums):
    topic_bar_graph = px.bar(
        column_sums, 
        x='topic', 
        y='value',
        title='Topic Breakdown of Social Media Posts', 
        color='topic',
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    topic_bar_graph.update_layout(
        font_family='Open Sans',
        font_color='black',
        title_x=0.5,
        legend_title="Topics",
        xaxis_title="Topic",
        yaxis_title="Number of Posts"
    )

    return topic_bar_graph


def engagement_statistics(time_frame, relative_date, start_date, end_date):
    # Pre-processing needed: Raw engagement - sum up all raw values
    # Normalized engagement - sum up all raw values, divide by the number of followers

    # Facebook (in current data pull): actual - likeCount, shareCount, commentCount, loveCount, 
        # wowCount, hahaCount, sadCount, angryCount, thankfulCount, careCount
    # Instagram (in current data pull): actual - favoriteCount, commentCount
    # Twitter (in current data pull): retweets, replies, likes, quote_count

    sm_df_filtered = sm_df

    if time_frame == 'relative':
        current_date = datetime.now()
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
        elif relative_date == 'All Dates':
            start_date = sm_df_filtered['authoredAt'].min()
        end_date = current_date.date()
    
    sm_df_filtered = sm_df[(sm_df['authoredAt'] >= start_date) 
                                & (sm_df['authoredAt'] <= end_date)]

    total_posts = len(sm_df_filtered.index)
    total_reactions = sum(sm_df_filtered['engagementRaw'])
                
    # for post in sm_df_filtered['raw']:
    #     id_index = post.find("'legacyId'")
    #     if id_index != -1:  # If 'id' is found
    #         substring = post[:id_index]
    #         substring += '}'
    #         post = substring
    #     post_dict = ast.literal_eval(post)

    return html.Div(id='engagement',
        children = [
            dbc.Container([ 
                dbc.Row(
                        [
                            html.H4(id='Engagement Statistics', children='Engagement Statistics', style={'fontStyle': 'italic'}),
                            html.Div(id='statistics', 
                                     children=[
                                        html.H5('Total Posts: ' + f'{total_posts:,}'),
                                        html.H5('Total Reactions: ' + f'{total_reactions:,}')
                                    ]
                                )
                        ], justify="center", align="center", className="h-50"         
                , style={"height": "100vh"}
            )
        ])
        ]
    )


            