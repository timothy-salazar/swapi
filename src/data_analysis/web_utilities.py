import requests
import json
import os
import pandas as pd

def get_json(url):
    """ Input:
            url: string - a valid url.
        Output:
            A dictionry containing the data located at "url".

        This function makes a GET request to "url". If the status code is 200
        (that is to say - if the GET request is successful), the function will
        load the json object returned by the API into one or more python
        dictionaries and return the result. Otherwise it will print an error
        message and write the skipped url to a log.
    """
    if url == None:
        return
    req = requests.get(url)
    time.sleep(3)
    if req.status_code == 200:
        return json.loads(req.content)
    else:
        print('ERROR: STATUS CODE {}'.format(req.status_code))
        log_skipped_url(url)

def log_skipped_url(url):
    """ Input:
            url: string - a url that was skipped for some reason
        Output:
            appends the url to the end of "skipped_url.log"
    """
    try:
        filename = os.path.join(os.environ['LOG_DIR'],'skipped_url.log')
    except KeyError:
        filename = os.path.join('..','..','assets','logs','skipped_url.log')
    with open(filename, 'a') as f:
        f.write(url+'\n')

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
    return '{}_{}'.format(usplit[-2], usplit[-1])

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
    cols = df.columns
    new_cols = df.columns[:13]
    r = []
    for i in results:
        # this will skip any columns that we add (which will not be valid keys)
        for c in cols[:9]:




        # ugly solution, but I want to get a minimum viable product
        for c in non_row_keys:
            for j in i[c]:
                new_cols.append(get_new_col_name(j))
                r.append(True)



def get_initial_df(column_list):
    return pd.DataFrame(columns=column_list)

def other_stuff(people_resource, df):
    add_to_df(df, people_resource['results'])
    people_resource = get_json(people_resource['next'])
    other_stuff(people_resource, df)


def stuff():
    base_url = 'http://swapi.co/api/people/'
    column_list = ['name','birth_year','eye_color','gender','hair_color',
                    'height','mass','skin_color','homeworld']
    df = get_initial_df(column_list)
    people_resource = get_json(base_url)
    other_stuff(people_resource)










    #
