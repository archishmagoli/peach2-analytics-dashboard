# Import required libraries
import numpy as np
import dash
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
                    style = {'border': '1px solid black'}
                ),
            ],
            style={'textAlign': 'left', 'width': '100%'}
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
    # Facebook (in raw data pull): actual - likeCount, shareCount, commentCount, loveCount, 
        # wowCount, hahaCount, sadCount, angryCount, thankfulCount, careCount
    
    # Instagram (in raw data pull): actual - favoriteCount, commentCount

    # Twitter (in raw data pull): retweets, replies, likes, quote_count

    total_posts = 0
    if time_frame == 'relative':
        total_posts = len(sm_df.index)
    else:
        total_posts = len(sm_df[(sm_df['authoredAt'] >= start_date) 
                                & (sm_df['authoredAt'] <= end_date)])
                
    # print(sm_df['raw'].dtype)

    # print("Time Frame: " + time_frame)
    # print("Relative Date: " + relative_date)
    # print("Start Date: " + str(start_date))
    # print("End Date: " + str(end_date))

    return html.Div(id='engagement',
            children=[
                html.H4(id='Engagement Statistics', children='Engagement Statistics', style={'fontStyle': 'italic'}),
                html.Div(id='statistics', children=[
                    html.H5('Total Posts: ' + str(total_posts))
                ])
            ],
            style={'textAlign': 'left', 'width': '100%'}
        )


            