import numpy as np
import pandas as pd

"""
This document contains some functions I used as a part of my exploratory
data analysis. I decided to do my early work in a jupyter notebook (since the
goal was to get something finished quickly), but I didn't like having to scroll
through a bunch of badly formated output.
There's a function in here to print some outputs in a few columns (instead of
in one long column), and a few other things.
"""


"""
These are utilities for printing things in a nice format
"""
def format_col_entry(x,i,j,w):
    a = '{}'.format(i).ljust(w-5)[:w-5]
    b = '{}: {}'.format('counts',j).ljust(w-5)[:w-5]
    return a+' '*5+b

def print_header(x, w, cols):
    a = '{}'.format(x.ljust(w-5))[:w-5]
    b = '{}'.format('counts'.ljust(w-5))[:w-5]
    print(*[a+' '*5+b for i in range(cols)] , sep='    |', end='\n')
    print('-'*72)

def get_unique_counts(df,x,sort=False):
    non_na_ind = ~df[x].isna()
    if not sort:
        return np.unique(df[x][non_na_ind], return_counts=True)
    else:
        u, c = np.unique(df[x][non_na_ind], return_counts=True)
        inx = np.argsort(c)
        return u[inx][::-1], c[inx][::-1]



def print_unique_counts(df,x,w=25,cols=2, col_sep='    |'): #
    """
    This gets the unique counts for a given column x, and prints the results in
    a number of neat columns of length w, separated by col_sep
    """
    print_header(x,w,cols)
    x_vals, x_counts = get_unique_counts(df, x, sort=True)
    l = [format_col_entry(x,i,j,w) for i,j in zip(x_vals, x_counts)]
    r = len(l)%cols
    if r != 0:
        l += [format_col_entry(x,'NaN',sum(df[x].isna()),w)]
    c = len(l)//cols
    col_list = [l[i:i+c] for i in range(0,len(l),c)]

    for i in range(c):
        print(*[col_list[j][i] for j in range(cols)], sep=col_sep, end='\n')
    if r == 0:
        print(format_col_entry(x,'NaN',sum(df[x].isna()),w))

"""
These are obsolete.
"""

def get_height_mask(df, g):
    return df.apply(lambda x: True if ((x.gender == g) and \
                    (x.height != 'unknown')) else False, axis = 1)

def union_not_nan_mask(df, col1, col2, val):
    if val.lower()[:3] in {'any', 'all'}:
        uindex = [True if not (pd.isna(df.loc[i][col1]) or pd.isna(df.loc[i][col2]))
                  else False for i in range(df.shape[0])]
        return uindex
    else:
        return df.apply(lambda x: True if ((x[col1] == val)\
                        and (x[col2] != 'unknown')\
                        and not (pd.isna(x[col2])))\
                        else False, axis = 1)
