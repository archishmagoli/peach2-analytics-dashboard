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

   # Convert to datetime
    weekly_df['weekAuthored'] = pd.to_datetime(weekly_df['weekAuthored'])

    # Extract date
    weekly_df = weekly_df.rename(columns={'weekAuthored' : 'Week Authored'})

    authors_to_remove = ['Survivor Corps', 'COVID-19 Long Haulers Support', 'A Voice for Choice']
    filtered_df = filtered_df[~filtered_df['author'].isin(authors_to_remove)]

    filtered_df = filtered_df.head(50)

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

    weekly_df.columns = ['Week Authored'] + [f'{i}' for i in range(1, len(weekly_df.columns))]
    weekly_df['Week Authored'] = weekly_df['Week Authored'].dt.strftime('%m/%d/%Y')

    all_children.append(html.Div(
            id='tf-idf-graph',
            style={'width': '50vw', 'maxHeight': '40vh', 'display': 'inline-block', 'verticalAlign': 'top', 'overflow': 'auto', 'border' : '1px solid black', 'marginBottom' : '2em'},  # Apply overflow auto to the container
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

    sm_df = sm_df[sm_df['author'].isin(interesting_authors)]

    posts = []

    for index, row in sm_df.iterrows():
        post_children = []
        post_children.append(html.Br())
        post_children.append(html.H5(row['platform'].title(), style={'fontWeight': 'bold'}))
        post_children.append(html.H6('Author: ' + row['author']))
        post_children.append(html.A('Link to Post', href=row['url']))
        post_children.append(html.H6(row['authoredAt'].date()))
        post_children.append(html.P(row['content']))

        posts.append(html.Div(children=post_children, style={'border': '1px solid black', 'height': '25em', 
                                            'minWidth': '20em', 'maxWidth': '30em', 'overflow': 'auto', 'margin': '1em', 'overflow':'scroll'}))
    
    all_children = []
    all_children.append(html.H4(children='Groups and Communities', style={"textAlign":"left", 'fontStyle' : 'italic'}))
    all_children.append(html.P(children='A collection of posts from various Facebook Groups.', style={'textAlign': 'left'}))
    all_children.append(html.Div(children=posts, style={'width': '50vw', 'overflow': 'auto', 'display' : 'flex'}))

    return html.Div(id='groups-communities', children = all_children, style={'justifyContent' : 'left'})

def symptoms(weekly_df):
    grouped_symptoms = {
        "fever": 0,
        "headache": 0,
        "cough": 0,
        "shortness_of_breath": 0,
        "fatigue": 0,
        "sore_throat": 0,
        "congestion": 0,
        "muscle_aches": 0,
        "nausea_vomiting": 0,
        "diarrhea": 0,
        "chills": 0,
        "chest_head_pressure": 0,
        "pink_eye": 0,
        "rash": 0,
        "dizziness": 0,
        "seizures": 0,
        "confusion": 0,
        "abdominal_pain": 0,
        "loss_of_appetite": 0,
        "muscle_joint_pain": 0,
        "difficulty_sleeping": 0,
        "feeling_disoriented": 0,
        "numbness_tingling": 0,
        "chest_pain": 0,
        "swelling_edema": 0,
        "bruising": 0,
        "loss_of_coordination": 0,
        "difficulty_speaking": 0,
        "frequent_urination": 0,
        "blood_in_urine": 0,
        "skin_discoloration": 0,
        "decreased_urination": 0,
        "swollen_glands": 0,
        "hair_loss": 0,
        "chapped_lips": 0,
        "puffy_eyes": 0,
        "weight_gain": 0,
        "hoarse_voice": 0,
        "mood_changes": 0,
        "cognitive_issues": 0,
        "leg_swelling": 0,
        "hair_thinning": 0,
        "dry_skin": 0,
        "weakness": 0,
        "tremors": 0,
        "depression": 0,
        "anxiety": 0,
        "irritability": 0,
        "insomnia": 0,
        "feeling_cold": 0,
        "feeling_hot": 0,
        "difficulty_breathing": 0,
        "chest_tightness": 0,
        "palpitations": 0,
        "lightheadedness": 0,
        "severe_headache": 0,
        "stroke_heart_attack": 0,
        "vision_loss": 0,
        "paralysis": 0,
        "aphasia": 0,
        "weakness_in_arms": 0,
        "weakness_in_legs": 0,
        "facial_droop": 0,
        "slurred_speech": 0,
        "difficulty_swallowing": 0,
        "decreased_sense_of_smell": 0,
        "decreased_sense_of_taste": 0
    }

    for index, row in weekly_df.iterrows():
        symptom_set = row['symptoms']
        for symptom in symptom_set:
            grouped_symptoms[symptom] += 1

    symptom_df = pd.DataFrame(grouped_symptoms.items(), columns=['symptom', 'count']).sort_values(by='count', ascending=False)

    symptom_graph = px.bar(
        symptom_df, 
        x='symptom', 
        y='count',
        title='Sharing of Symptoms', 
        color='symptom',
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    symptom_graph.update_layout(
        font_family='Open Sans',
        font_color='black',
        title_x=0.5,
        legend_title="Symptoms",
        xaxis_title="Symptom",
        yaxis_title="Number of Weeks Observed"
    )

    return html.Div(id='symptoms',
        children=[
            html.H4(children='Sharing of COVID Symptoms', style={'textAlign' : 'left', 'fontStyle' : 'italic'}),
            html.P(children='Displays the types of symptoms mentioned across social media platforms.', style={'textAlign' : 'left'}),
            dcc.Graph(
                id='symptom-bar-graph',
                figure = symptom_graph,
                style = {'border': '1px solid black', 'width': '30vw'}
            ),
        ],
        style={'marginRight' : '5em'}
    )

def news_engagement(sm_df):

    ## TO-DO: Questions about COVID; reactions to news posts, topic analysis -- informational news and institutional posts

   # Drop NaN values from the 'labels' column
    sm_df.dropna(subset=['labels'], inplace=True)

    # Convert NaN values to empty string in the 'labels' column
    sm_df['labels'].fillna('', inplace=True)

def news_engagement(sm_df):
    all_children = []
    all_children.append(html.H4(children='News and Institutions', style={"textAlign":"left", 'fontStyle' : 'italic'}))
    all_children.append(html.P(children="'Viral' News Cycles: recording post trends from news and institutional accounts.", style={'textAlign': 'left'}))

    # Filter the DataFrame
    post_count_df = sm_df[sm_df['labels'].apply(lambda x: 'news' in x or 'institutional' in x)]

    # Calculate post counts
    post_count = post_count_df.groupby('authoredAt').size().rolling(window=7).mean()

    figure = px.line(x=post_count.index, y=post_count.values,
                        title='News + Institutional Posts Over Time', 
                        labels={'authoredAt':'Date', 'value': 'Post Count'}
                    )

    figure.update_traces(line_color='#0053a0')
    figure.update_layout(
        title='News + Institutional Posts Over Time',
        xaxis_title='Date',
        yaxis_title='Post Count',
        legend_title_text='Post Count',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font_family='Open Sans',
        font_color='black',
        title_x=0.5
    )
    
    all_children.append(html.Div(children=dcc.Graph(figure=figure), style={'border' : '1px solid black'}))
    
    return html.Div(id='news-engagement', children=all_children, style={'width': '45vw'})


def news_posts(sm_df):
    all_children = []

    post_count_df = sm_df[sm_df['labels'].apply(lambda x: 'news' in x or 'institutional' in x)]
    posts = []

    for index, row in post_count_df.iterrows():
        post_children = []
        post_children.append(html.Br())
        post_children.append(html.H5(row['platform'].title(), style={'fontWeight': 'bold'}))
        post_children.append(html.H6('Author: ' + row['author']))
        post_children.append(html.A('Link to Post', href=row['url']))
        post_children.append(html.H6(row['authoredAt'].date()))
        post_children.append(html.P(row['content']))

        posts.append(html.Div(children=post_children, style={'border': '1px solid black', 'height': '25em', 
                                            'minWidth': '20em', 'maxWidth': '30em', 'overflow': 'auto', 'margin': '1em', 'overflow':'scroll'}))
    
    all_children.append(html.Br())
    all_children.append(html.P(children="Informational News + Institutional posts across all platforms.", style={'textAlign': 'left'}))
    all_children.append(html.Div(children=posts, style={'maxWidth': '80vw', 'overflowX': 'auto', 'display' : 'flex'}))

    return html.Div(id='news-posts', children = all_children, style={'justifyContent' : 'left'})

