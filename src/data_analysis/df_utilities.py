import pandas as pd
import numpy as np


def get_new_col_name(url):
    """ Input:
            url: string - the url contained in the 'films','species',
            'starships', or 'vehicles' field of a "people" resource.
        Output:
            returns a string that can be used as a new column, with the format:
            [category]_[num], where 'category' is a category such as 'films',
            and 'num' is an integer.
    """
    usplit = url.split('/')
    return '{}_{}'.format(usplit[-3], usplit[-2])

def add_to_df(df, results):
    """ Input:
            df: A Pandas DataFrame
            results: list of dictionaries.
        Output:
            df: A Pandas Dataframe with the results appended as a new row,
                and with columns added for new films, starships, etc.
    """
    # dictionary keys that aren't being made directly into rows (lists)
    non_row_keys = ['films','species','starships','vehicles']

    for i in results:
        row_dict = dict()
        # grabs the fields that can be put into our df w/o modification
        for c in df.columns[:9]:
            row_dict[c] = i[c]
        # ugly solution, but I want to get a minimum viable product.
        # takes values from fields containing lists, makes columns for each
        # value, and sets these to True.
        for c in non_row_keys:
            for j in i[c]:
                row_dict[get_new_col_name(j)] = True
        df = df.append([row_dict], sort=False, ignore_index=True)
    return df

def get_initial_df(column_list):
    """ Input:
            column_list: list of strings
    """
    return pd.DataFrame(columns=column_list)




#
