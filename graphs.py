# Import required libraries
import numpy as np
import ast, json
from datetime import datetime
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dash_table
import re

def hot_topics(column_sums):
    return html.Div(id='hot_topics',
            children=[
                html.H4(id='Hot Topics', children='Keywords and Trends', style={'fontStyle': 'italic'}),
                dcc.Graph(
                    id='topic-bar-graph',
                    figure = px.bar(
                        column_sums, 
                        x=column_sums['topic'],
                        y=column_sums['value'],
                        title='Keyword Breakdown of Social Media Posts',
                        color_discrete_sequence=px.colors.qualitative.Prism),
                    style = {'border': '1px solid black', 'width': '5em'}
                ),
            ],
            style={'textAlign': 'center', 'margin': '1em'}
        )

def topic_bar_graph(column_sums):
    topic_bar_graph = px.bar(
        column_sums, 
        x='topic', 
        y='value',
        title='Keyword Breakdown of Social Media Posts', 
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
    total_posts = len(filtered_df.index)
    total_reactions = sum(filtered_df['engagementRaw'])
    platformList = list(filtered_df['platform'].unique())

    facebookLikeCount = 0
    facebookShareCount = 0
    facebookCommentCount = 0
    facebookWowCount = 0
    facebookHahaCount = 0
    facebookSadCount = 0
    facebookLoveCount = 0
    facebookAngryCount = 0
    facebookThankfulCount = 0
    facebookCareCount = 0

    instagramFavoriteCount = 0
    instagramCommentCount = 0

    twitterRetweets = 0
    twitterReplies = 0
    twitterLikes = 0
    twitterQuoteCount = 0
                
    for index, row in filtered_df.iterrows():
        if row['platform'] == 'twitter':
            post = row['raw']
            twitterRetweets += post['retweets']
            twitterReplies += post['replies']
            twitterLikes += post['likes']
            twitterQuoteCount += post['quote_count']

        elif row['platform'] == 'facebook':
            post = row['raw']['statistics']['actual']
            facebookLikeCount += post['likeCount']
            facebookShareCount += post['shareCount']
            facebookCommentCount += post['commentCount']
            facebookLoveCount += post['loveCount']
            facebookWowCount += post['wowCount']
            facebookHahaCount += post['hahaCount']
            facebookSadCount += post['sadCount']
            facebookAngryCount += post['angryCount']
            facebookThankfulCount += post['thankfulCount']
            facebookCareCount += post['careCount']


        else:
            post = row['raw']['statistics']['actual']
            instagramFavoriteCount += post['favoriteCount']
            instagramCommentCount += post['commentCount']

    values = []
    values.append(html.Br())
    values.append(html.H4(f'{total_posts:,} ' + 'Total Posts'))
    values.append(html.H4(f'{total_reactions:,} ' + 'Total Reactions'))

    if 'facebook' in platformList:
        values.append(html.Div(children=[html.Br(),
                        html.H5('Facebook Reactions'),
                        html.H6('Like Count 👍: ' + f'{facebookLikeCount:,} '),
                        html.H6('Share Count 🫂: ' + f'{facebookShareCount:,} '),
                        html.H6('Comment Count 💬: ' + f'{facebookCommentCount:,} '),
                        html.H6('Heart Count ❤️: ' + f'{facebookLoveCount:,} '),
                        html.H6('Wow Count 😯: ' + f'{facebookWowCount:,} '),
                        html.H6('Laugh Count 😂: ' + f'{facebookHahaCount:,} '),
                        html.H6('Sad Count 😢: ' + f'{facebookSadCount:,} '),
                        html.H6('Angry Count 😡: ' + f'{facebookAngryCount:,} '),
                        html.H6('Thankful Count 🌸: ' + f'{facebookThankfulCount:,} '),
                        html.H6('Care Count 🥰: ' + f'{facebookCareCount:,} '),
                        html.Br()
                    ], style={'border': '1px solid black'}))

    if 'instagram' in platformList:
        values.append(html.Br())
        values.append(html.Div(children = [html.Br(), 
                                           html.H5('Instagram Reactions'), 
                                           html.H6('Favorite Count ❤️: ' + f'{instagramFavoriteCount:,} '),
                                           html.H6('CommentCount 💬: ' + f'{instagramCommentCount:,} '), html.Br()], style={'border': '1px solid black'}))

    if 'twitter' in platformList:
        values.append(html.Br())
        values.append(html.Div(children = [html.Br(),
                                html.H5('Twitter Reactions'), 
                                html.H6('Retweet Count 🔄: ' + f'{twitterRetweets:,} '),
                                html.H6('Reply Count 💬: ' + f'{twitterReplies:,} '),
                                html.H6('Like Count 👍: ' + f'{twitterLikes:,} '),
                                html.H6('Quote Count 🗣️: ' + f'{twitterQuoteCount:,} '), html.Br()], style={'border': '1px solid black'}))
        
    values.append(html.Br())

    return html.Div(id='engagement',
        children = [
            dbc.Container([ 
                dbc.Row(
                        [
                            html.H4(id='Engagement Statistics', children='Engagement Statistics', style={'fontStyle': 'italic'}),
                            html.P('The number of reactions and comments across all platforms.'),
                            html.Div(id='statistics', 
                                     children=values, style={'border': '1px solid black'}), 
                        ], justify="center", align="center", className="h-50"         
                , style={"height": "100vh", "alignItems": "center"}
            )
        ], style={'maxWidth': '100vw', "margin": "1em"})
        ],
        style={'marginRight' : '1em'}
    )

def posts(sm_df):
    posts = []
    filtered_df = sm_df.sort_values(by='engagementRaw', ascending=False).head(20).reset_index()

    for index, row in filtered_df.iterrows():
        post_children = []
        post_children.append(html.Br())
        post_children.append(html.H5(row['platform'].title(), style={'fontWeight': 'bold'}))
        post_children.append(html.H6('Author: ' + row['author']))
        post_children.append(html.A('Link to Post', href=row['url']))
        post_children.append(html.H6(row['authoredAt'].date()))

        if row['platform'] == 'instagram':
            favorites = row['raw']['statistics']['actual']['favoriteCount']
            comments = row['raw']['statistics']['actual']['commentCount']
            post_children.append(html.P('❤️' + f'{favorites:,} ' + ' | ' + '💬' + f'{comments:,} '))
        elif row['platform'] == 'twitter':
            likes = row['raw']['likes']
            replies = row['raw']['replies']
            retweets = row['raw']['retweets']
            post_children.append(html.P('🔄' +f'{retweets:,} ' + ' | ' + '👍' + f'{likes:,} ' + ' | ' + '💬' + f'{replies:,} ' + '|'))
        else:
            likes = row['raw']['statistics']['actual']['likeCount']
            comments = row['raw']['statistics']['actual']['commentCount']
            post_children.append(html.P('👍' + f'{likes:,}' + ' | ' + '💬' +f'{comments:,} '))

        post_children.append(html.P(row['content']))

        posts.append(html.Div(children=post_children, style={'border': '1px solid black', 'height': '25em', 'maxWidth': '30em', 
                                            'minWidth': '20em', 'overflow': 'auto', 'margin': '1em'}))

    return html.Div(id='posts', children=posts, style={'display': 'flex', 'maxWidth': '100vw', 
                                                       'overflowX': 'auto'})

def tf_idf(sm_df, weekly_df):
    keywords = []

    # Assuming 'weekly_df' is your DataFrame containing keywords
    for column in weekly_df.columns:
        for index, value in weekly_df[column].items():
            if isinstance(value, str) and any(char.isalpha() for char in value):
                keywords.append(value)

    # Escape special characters in keywords
    escaped_keywords = [re.escape(keyword) for keyword in keywords]

    # Create regex pattern to match any of the keywords
    pattern = '|'.join(escaped_keywords)

    # Filter sm_df based on keywords
    filtered_df = sm_df[sm_df['actualText'].str.contains(pattern)].reset_index(drop=True)

    weekly_df['weekAuthored'] = pd.to_datetime(weekly_df['weekAuthored'])
    weekly_df['weekAuthored'] = weekly_df['weekAuthored'].dt.strftime('%m/%d/%Y').copy()
    weekly_df = weekly_df.rename(columns={'weekAuthored' : 'Week Authored'})

    authors_to_remove = ['Survivor Corps', 'COVID-19 Long Haulers Support', 'A Voice for Choice']
    filtered_df = filtered_df[~filtered_df['author'].isin(authors_to_remove)]

    filtered_df = filtered_df.head(100)

    posts = []

    for index, row in filtered_df.iterrows():
        post_children = []
        post_children.append(html.Br())
        post_children.append(html.H5(row['platform'].title(), style={'fontWeight': 'bold'}))
        post_children.append(html.H6('Author: ' + row['author']))
        post_children.append(html.A('Link to Post', href=row['url']))
        post_children.append(html.H6(row['authoredAt'].date()))
        post_children.append(html.P(row['content']))

        posts.append(html.Div(children=post_children, style={'border': '1px solid black', 'height': '25em', 'maxWidth': '30em', 
                                            'minWidth': '20em', 'overflow': 'auto', 'margin': '1em', 'overflow':'scroll'}))
    
    all_children = []

    all_children.append(html.H4('Hot Topics 🔥', style={'fontStyle': 'italic'}))
    all_children.append(html.P('A list of the top 20 keywords mentioned in posts across all platforms over a 1-week time frame.'))
    all_children.append(html.Div(
            id='tf-idf-graph',
            style={'width': '50vw', 'height': '40vh', 'overflow': 'auto', 'border' : '1px solid black'},  # Apply overflow auto to the container
            children=[
                dash_table.DataTable(
                    id='table',
                    columns=[{'name': str(col), 'id': str(col)} for col in weekly_df.columns],
                    data=weekly_df.to_dict('records'),
                    style_table={'overflowX': 'auto', 'overflowY': 'auto', 'width': '100%'},  # Set table width to 100%
                    style_cell={
                        'whiteSpace': 'normal',
                        'height': 'auto',
                        'fontFamily': 'inherit',
                        'textAlign': 'center',
                        'fontFamily': 'Open Sans, verdana, arial, sans-serif'
                    },
                    style_header={
                        'fontWeight': 'bold'  # Make the header row bold
                    }
                )
            ]
        ))
    all_children.append(html.Br())
    all_children.append(html.H4('Related Posts', style={'fontStyle': 'italic'}))
    all_children.append(html.P('A collection of the posts that contain one or more of the related keywords!'))
    all_children.append(html.Div(children=posts, style={'width': '50vw', 'overflow': 'auto', 'display' : 'flex'}))
    
    return html.Div(id='tf-idf', children = all_children)


def groups_and_communities(sm_df):
    interesting_authors = ['COVID-19 Long Haulers Support', 'Survivor Corps', 
                           'Vaccines save lives', 'COVID-19 Novel Coronavirus FACTS', 
                           '¡MÉDICOS POR LA VERDAD!', 'Black News Network (BNN)', 
                           'COVID19: Real Talk from Health Care Workers around the Globe', 
                           'Black Educators', 'Covid Wellness Clinic', 
                           'Coronavirus Updates for: Statesboro, Georgia & Surrounding Counties', 
                           'Athens GA COVID-19 Resources and Discussion', 'Georgia Trump Republicans', 
                           "Skip Mason's Vanishing Black Atlanta History", 'DeKalb Strong', 
                           'COVID-19 Watch North GA w/ Help & Resources', 
                           'Albany, GA Area Happenings Over 21', 'Albany GA: Home Is Where The Heart Is', 
                           'Type 1 Diabetes Recipes & Food Ideas', 
                           'Kimono My House (Virtual House Concerts)', 'Dank Diabetes Memes Diabuddies', 
                           'America First Tea Party', 'The Prayer Wall', 'TERMINÓ 🧑\u200d🦽🧑\u200d🦽🧑\u200d🦽🧑\u200d🦽', 
                           'Coronavirus Updates from NBC News']

    sm_df = sm_df[sm_df['author'] in interesting_authors]
    