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
                html.H4(id='Hot Topics', children='Keywords', style={'fontStyle': 'italic'}),
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
            style={'textAlign': 'center', 'width': '75%'}
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


def engagement_statistics(filtered_df):
    # Pre-processing needed: Raw engagement - sum up all raw values
    # Normalized engagement - sum up all raw values, divide by the number of followers

    # Facebook (in current data pull): actual - likeCount, shareCount, commentCount, loveCount, 
        # wowCount, hahaCount, sadCount, angryCount, thankfulCount, careCount
    # Instagram (in current data pull): actual - favoriteCount, commentCount
    # Twitter (in current data pull): retweets, replies, likes, quote_count

    total_posts = len(filtered_df.index)
    total_reactions = sum(filtered_df['engagementRaw'])
                
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
                                        html.H4(f'{total_posts:,} ' + 'Total Posts'),
                                        html.H4(f'{total_reactions:,} ' + 'Total Reactions')
                                    ]
                                )
                        ], justify="center", align="center", className="h-50"         
                , style={"height": "100vh", "alignItems": "center"}
            )
        ], style={'border': '1px solid black', 'max-width': '100vw', "margin": "1em"})
        ]
    )

def posts(sm_df):
    posts = []
    filtered_df = sm_df.sort_values(by='engagementRaw', ascending=False).head(20).reset_index()
    for index, row in filtered_df.iterrows():       
        posts.append(html.Div(children=[
                                html.H5(row['platform'].title(), 
                                        style={'fontWeight': 'bold'}),
                                html.A('Link to Post', href=row['url']),
                                html.P(row['authoredAt']),
                                html.P(row['content']),
                                ], style={'border': '1px solid black', 'height': '25em', 'max-width': '30em', 
                                            'min-width': '20em', 'overflow': 'auto', 'margin': '1em'}
        ))

    return html.Div(id='posts', children=posts, style={'display': 'flex', 'max-width': '100vw', 
                                                       'overflow-x': 'auto'})


            