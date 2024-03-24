# Import required libraries
import pandas as pd

def process_pickle():
    # Load the dataframe
    sm_df = pd.read_pickle('updated_posts_vader.pkl')

    # authoredAt column manipulation for timeseries grouping
    sm_df['authoredAt'] = pd.to_datetime(sm_df['authoredAt'])
    sm_df['authoredAt'] = sm_df['authoredAt'].dt.date

    return sm_df