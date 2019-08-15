import requests
import json
import os
import pandas as pd
import time
#from . import df_utilities

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
    print("Visiting url: {}".format(url))
    if url == None:
        return
    req = requests.get(url)
    # it's always courteous to add a delay when pulling from a public source
    time.sleep(1.5)
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
        filename = os.path.join('assets','logs','skipped_url.log')
    with open(filename, 'a') as f:
        f.write(url+'\n')

def get_asset_path(*args):
    """ Inputs:
            *args: a list of strings corresponding to zero or more sub
                directories within the "assets" directory and a filename.
        Output:
            Returns absolute path to the specified location within the assets
            directory.
    """
    a = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(a, '..','..','assets',*args))

def url_to_val_dict(api_cat):
    """ Input:
            api_cat: string - the category we want to build dictionary for
        Output:
            d: dictionary - a dictionary with urls as keys and the names of the
                resource located at those urls as the corresponding values.

            Also writes the dictionary to a json file, so that we don't need
            to build it from the API more than once.
    """
    url = 'https://swapi.co/api/{}/'.format(api_cat)
    d = dict()
    json_path = get_asset_path('json','{}_dict.json'.format(api_cat))
    if not os.path.exists(json_path):
        while url != None:
            r = get_json(url)
            for i in r['results']:
                d[i['url']]=i['name']
            url = r['next']
        with open(json_path, 'w') as f:
            f.write(json.dumps(d))
    else:
        with open(json_path, 'r') as f:
            d = json.load(f)
            print('Json loaded!')
    return d

    #
