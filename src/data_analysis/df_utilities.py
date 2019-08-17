import pandas as pd
import numpy as np
from . import web_utilities

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
    for c in df.columns[10:]:
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

        This works by making a new dataframe for each row. The first 10 columns
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
    non_row_keys = ['films','starships','vehicles']
    for i in results:
        row_dict = dict()
        # grabs the fields that can be put into our df w/o modification
        for c in df.columns[:10]:
            # the 'species' field is a list, but it contains either 1 or 0
            # values in all cases. No hybrids in Star Wars I guess.
            # using 'unknown' following this API's conventions.
            if c == 'species':
                row_dict[c] = i[c][0] if len(i[c]) > 0 else 'unknown'
            else: row_dict[c] = i[c]
        # ugly solution, but I want to get a minimum viable product.
        # takes values from fields containing lists, makes columns for each
        # value, and sets these to True.
        for c in non_row_keys:
            for j in i[c]:
                row_dict[j] = True
        # special case - seeing what happens
        # row_dict['species'] = i['species']
        df = df.append([row_dict], sort=False, ignore_index=True)
    df = fill_in_with_false(df)
    return df

def get_initial_df():
    """ Input:
            None
        Output:
            A Pandas DataFrame. The column names are the keys for the first
            10 fields in the Star Wars API People resource.
    """
    column_list = ['name','birth_year','eye_color','gender','hair_color',
                'height','mass','skin_color','homeworld', 'species']
    return pd.DataFrame(columns=column_list)

def star_date_to_float(x):
    """ Input:
            x: string - a date using the Star Wars calendar, or 'unknown'.

        Output:
            Either the date as a negative float if x ended in BBY, a positive
            float if x ended in ABY, or NaN if x was 'unknown'

    If the string ends with BBY, it indicates that the person was born before
    the Battle of Yavin. If the string ends with ABY it indicates that the
    person was born after tbe Battle of Yavin. There are no ABY dates included
    in the birth_year column, but I'll write this to handle the ABY case anyway,
    I might need it later.
    """
    if x[-3:] == 'BBY': return -float(x[:-3])
    elif x[-3:] == 'ABY': return float(x[:-3])
    else: return np.NaN

def format_birth_year(s):
    """ Input:
            s: Series - a Pandas Series containing strings. These are dates
                ending in BBY or ABY, or 'unknown'
        Output:
            A series containing the same dates as floats. If the original dates
            ended in BBY, they will be negative. If the original string was
            'unknown', it will be replaced with NaN
    """
    if s.dtype == 'float64':    # prevent this from raising an error if run
        return s                # multiple times
    return s.apply(lambda x: star_date_to_float(x))

def world_url_to_name(s):
    """ Input:
            s: Series - a Pandas Series containing strings. These are urls
                corresponding to planets.
        Output:
            A series in which the urls have been replaced with the name of the
            planet located at that location.
    """
    world_dict = web_utilities.url_to_val_dict('planets')
    return s.apply(lambda x: world_dict[x] if x[:8] == 'https://' else x)

def urls_to_names(df, col_name=None):
    """ Input:
            df: Pandas DataFrame
            col_name: None or string. If none, replaces the column names.
                Otherwise replaces the entries in column 'col_name'
        Output:
            df: Pandas DataFrame

    Some of the fields returned by the Star Wars API are lists, and we expanded
    these into new columns. These lists contain urls that refer to resources
    located elsewhere, so I took each new url and turned it into a column -
    with a value of True or False depending on whether it was applicable to a
    given row.
    This function first builds a dictionary in which the keys are urls, and the
    values are names. So "https://swapi.co/api/films/1/" would correspond to the
    value "A New Hope", etc.
    It then goes through the new columns we added, converts the unintuitive url
    column names to values that make sense, and updates the dataframe with them.
    """
    d = dict()
    for i in ['planets','films','species','vehicles','starships']:
        d = {**d, **web_utilities.url_to_val_dict(i)}
    if not col_name:
        new_cols = [d[df.columns[i]] if df.columns[i][:8]=='https://' \
                    else df.columns[i] for i in np.arange(10,df.shape[1],1)]
        df.columns = list(df.columns[:10]) + new_cols
        return df
    else:
        df[col_name] = [d[i] if i[:8]=='https://' else i for i in df[col_name]]
        return df

def replace_unknown(df, cols):
    for i in cols:
        df[i] = [j if j != 'unknown' else np.nan for j in df[i]]
    return df

def replace_na(df, cat_rep):
    for i in cat_rep:
        c, d = i[0],i[1]
        df[c] = [d[j] if j in d.keys() else j for j in df[c]]
    return df

def cleanup(df):
    """ Input:
            df: Pandas DataFrame
        Output:
            df: Pandas DataFrame
    Runs a number of functions to clean up the dataframe. This includes
    replacing the url in the "homeworld" field with the actual name of the
    planet, replacing the urls in the column names with the film, species,
    vehicle, and starship names that they're standing in for, and formatting
    the "birth_year" column.

    """
    float_cols = ['birth_year','height','mass','skin_color']
    # Pandas will interpret 'n/a' as NaN if it reads this dataframe
    # from a csv. 'n/a' is significant, however - it doesn't mean
    # that there isn't a value there.
    category_replacements = [['eye_color',{'n/a':'no eyes'}],
                            ['gender',{'n/a':'no gender'}],
                            ['hair_color',{'n/a':'no hair'}]]
    df['birth_year'] = format_birth_year(df['birth_year'])
    df = urls_to_names(df, col_name='homeworld')
    df = urls_to_names(df)
    df = urls_to_names(df, col_name='species')
    df = replace_unknown(df, float_cols)
    df = replace_na(df,category_replacements)
    return df

def build_dataframe(people_resource=None, df=None):
    """ Input:
            people_resource: dict - the People resource returned by the Star
                Wars API.
            df: Pandas DataFrame - a dataframe which initially has the keys for
                the first 10 fields in the People dict as its columns. The
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
    if not people_resource:
        df = get_initial_df()
        people_resource = web_utilities.get_json(base_url)
    else:
        people_resource = web_utilities.get_json(people_resource['next'])
    if people_resource:
        df = add_to_df(df, people_resource['results'])
        df = build_dataframe(people_resource, df)
    return df




#
