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

def fill_in_with_false(df):
    """ Input:
            df: Pandas DataFrame
        Output:
            df: Pandas DataFrame
        In the add_to_df() function, the lists contained in the 'films',
        'species', 'starships', and 'vehicles' fields are expanded to columns
        containing True (if the value was present in that person's dict), or
        NaN. This goes through and replaces the NaNs we produced in add_to_df()
        with False
    """
    for c in df.columns[9:]:
        df[c][df[c].isna()] = False
    return df

def add_to_df(df, results):
    """ Input:
            df: A Pandas DataFrame
            results: list of dictionaries.
        Output:
            df: A Pandas Dataframe with the results appended as a new row,
                and with columns added for new films, starships, etc. The
                values for these new columns will be True if valid for the
                person in that row, False otherwise.

        This works by making a new dataframe for each row. The first 9 columns
        contain the data that can be translated directly from the dictionary
        returned from the Star Wars API. A new column is created for each item
        in 'non_row_keys'. For example, the 'starships' field in the dictionary
        might contain starships 1, 12, and 22. New columns called "starships_1",
        "starships_12", and "starships_22" would be created and given the value
        True.
        Pandas is nice because we can append this row dataframe - which contains
        columns that are not present in the original dataframe - and Pandas
        simply fills in the missing values that ensue with NaNs. Because of
        this, we don't need to know the name of all the columns in our dataframe
        before we begin!
        The NaNs are replaced with False by the fill_in_with_false() function.
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
    df = fill_in_with_false(df)
    return df

def get_initial_df(column_list):
    """ Input:
            None
        Output:
            A Pandas DataFrame. The column names are the keys for the first
            9 fields in the Star Wars API People resource.
    """
    column_list = ['name','birth_year','eye_color','gender','hair_color',
                'height','mass','skin_color','homeworld']
    return pd.DataFrame(columns=column_list)

def build_dataframe(people_resource=None, df=None):
    """ Input:
            people_resource: dict - the People resource returned by the Star
                Wars API.
            df: Pandas DataFrame - a dataframe which initially has the keys for
                the first 9 fields in the People dict as its columns. The
                fields that contain lists are expanded into new columns.
        Output:
            df: Pandas DataFrame - a dataframe containing the People data from
                the Star Wars API.
    This function will create a Pandas DataFrame, visit the base url for the
    Star Wars API People resources, and then call itself using the "next" field
    in the response returned by the GET request, (which contains the url of the
    next page). This allows us to recursively visit each People page in the
    API, and put the data into a Pandas DataFrame.
    """
    base_url = 'http://swapi.co/api/people/'
    if not df:
        df = get_initial_df(column_list)
        people_resource = web_utilities.get_json(base_url)
    else:
        people_resource = web_utilities.get_json(people_resource['next'])
    df = add_to_df(df, people_resource['results'])
    df = build_dataframe(people_resource, df)
    return df


#
