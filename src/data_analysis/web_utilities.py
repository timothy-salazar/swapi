import requests
import json
import os
import pandas as pd
from . import df_utilities

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
        df = df_utilities.get_initial_df(column_list)
        people_resource = get_json(base_url)
    else:
        people_resource = get_json(people_resource['next'])
    df = df_utilities.add_to_df(df, people_resource['results'])
    df = df_utilities.build_dataframe(people_resource, df)
    return df






    #
