import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from PIL import Image
from astropy.visualization import hist
from scipy.stats import norm
import os

def axis_style(ax,title,alpha=.1):
    asset_dir = os.environ['ASSET_DIR']
    fpath = os.path.join(asset_dir,'fonts','starjedi','Starjedi.ttf' )
    prop = fm.FontProperties(fname=fpath)
    ax.patch.set_facecolor((1, 1, 1, alpha))
    ax.patch.set_linewidth(2)
    ax.tick_params(axis='both', colors='white')
    ax.set_title(title, fontproperties=prop, color='white', size='xx-large')
    ax.spines['left'].set_color('white')
    ax.spines['bottom'].set_color('white')
    return ax

def make_it_cool(fig, col_vals, bbox, main_title, mt_size,
                    alpha=.1):
    asset_dir = os.environ['ASSET_DIR']
    fpath = os.path.join(asset_dir,'fonts','stjelogo','Stjldbl2.ttf' )
    prop = fm.FontProperties(fname=fpath)
    fig.get_children()[1].axis("off")
    fig.get_children()[1].set_position(bbox)
    if len(fig.get_children()) > 3:
        for i, title in zip(fig.get_children()[2:], col_vals):
            i = axis_style(i,title,alpha)
    else:
        pass
    fig.suptitle(main_title,fontproperties=prop,
                 color='#FFE81F', fontsize=mt_size)
    return fig

def intersect_not_nan_mask(df, col1, col2, val='any'):
    """ Input:
            df: Pandas DataFrame
            col1: first column of intersection
            col2: second column of intersection
            val: the values in column 1 for which we want a mask
        Output:
            mask of bool values.
        Example:
            If we were interested in the "species" and "height" columns of our
            dataframe, and we wanted to get the rows where species AND height
            both had valid (not NaN or "unknown") values, we could pass this
            function df=df, col1="species", col2="height"
            If we wanted a little more refinement, we could ask for the rows
            where "species" is "Human" and height is not NaN or "unknown" by
            passing this function df=df, col1="species", col2="height",
            val="Human".
    I tried to make this readable, but it still might be a little
    cryptic. Using lambda functions and apply is a lot faster than
    iterating through the items in the dataframe though (moving from pandas
    space into python space always slows us down a lot)
    """
    if val.lower()[:3] in {'any', 'all'}:
        return df.apply(lambda x: True if not (pd.isna(x[col1]) \
                or (x[col1]=='unknown') or pd.isna(x[col2]) \
                or (x[col2]=='unknown')) else False, axis=1)
    else:
        return df.apply(lambda x: True if not (pd.isna(x[col1]) \
            or (x[col1]=='unknown') or pd.isna(x[col2]) \
            or (x[col2]=='unknown') or (x[col1]!=val)) else False, axis=1)



def match_hist_color(fig):
    """ Input:
            fig: matplotlib figure
        Output:
            color: color
    For the last axes created on the figure, retrieves the last polygon drawn
    and returns the facecolor. So, if a histogram was the last item plotted,
    this will return the color used to fill the bins.
    """
    p_list = [i for i in fig.axes[-1].get_children()
         if type(i) == matplotlib.patches.Polygon]
    return p_list[-1].get_facecolor()

def get_scaled_img(fig,imname='starfield.png'):
    """
    """
    fig_size = fig.get_size_inches()*fig.dpi
    impath = os.path.join(os.environ['ASSET_DIR'],'images',imname)
    img = Image.open(impath)
    img_size = img.size
    a = [i - j for i,j in zip(fig_size, img_size)]
    b = [0,0]
    small_axis = np.argmax(a)
    crop_axis = np.argmin(a)
    b[small_axis] = img_size[small_axis]
    crop_size = int((img_size[small_axis]/fig_size[small_axis])*fig_size[crop_axis])
    b[crop_axis] = crop_size
    box = (0, 0, b[0], b[1])
    img = img.resize((int(fig_size[0]),int(fig_size[1])),box = box)
    return img

def plot_in_cols(quant_list, col1_vals, graph_width, hmin, hmax,
                 bin_val, htype, title_str):
    clen = len(col1_vals)
    ax_list = []
    plot_height = clen // 2 + clen % 2
    fig = plt.figure(figsize=(graph_width,plot_height*5))
    img = get_scaled_img(fig)
    ax_im = plt.imshow(img)
    plt.axis('off')
    for v1, v2, i in zip(quant_list, col1_vals, range(clen)):
        if len(ax_list)==0: ax = fig.add_subplot(plot_height,2,i+1, alpha=0)
        else:
            ax = fig.add_subplot(plot_height,2,i+1, alpha=0,
                                sharex=ax_list[0],sharey=ax_list[0])
        ax_list.append(ax)
        n, bins, patches = hist(v1, bins=bin_val, ax=ax,
                                histtype=htype, alpha=0.7, density=True)
        mu, std = norm.fit(v1)
        x = np.linspace(hmin, hmax, 100)
        y = norm.pdf(x, mu, std)
        c = match_hist_color(fig)
        l = ax.plot(x, y, color=c, linewidth=3, alpha=1)
        ax.set_title(title_str.format(col1_vals[i]))
    return fig, ax_list

def plot_single_axis(quant_list, col1_vals, graph_width, hmin, hmax,
                     bin_val, htype, add_legend=True):
    clen = len(col1_vals)
    fig, ay = plt.subplots(figsize=(graph_width,graph_width))
    img = get_scaled_img(fig)
    ay.imshow(img)
    ax = fig.add_subplot(111)
    print(hmin, hmax)
    for v1, v2, i in zip(quant_list, col1_vals, range(clen)):
        n, bins, patches = hist(v1, bins=bin_val, histtype=htype, alpha=0.7,
                                density=True, label=col1_vals[i])
        mu, std = norm.fit(v1)
        x = np.linspace(hmin,hmax,100)
        y = norm.pdf(x, mu, std)
        c = match_hist_color(fig)
        l = ax.plot(x, y, color=c, linewidth=2,alpha=1, zorder=15+i)
        ax = axis_style(ax,"", alpha=0)
        ax.tick_params('both',labelsize=16)
    if add_legend:
        asset_dir = os.environ['ASSET_DIR']
        fpath = os.path.join(asset_dir,'fonts','starjedi','Starjedi.ttf' )
        prop = fm.FontProperties(fname=fpath,size=22)
        plt.legend(loc='upper right',prop=prop, bbox_to_anchor=[1,.95])
    return fig, ax, patches

def plot_df_hist(df, col1, col1_vals, col2='height', graph_width=10,
                    plot_type='cols', bin_val='freedman', htype='stepfilled',
                    title_str='{}', bbox = [.05,.05,.95,.95],
                    main_title="Height Across Species",mt_size=36):
    ax_list = []
    hmax = 0
    hmin = 500
    quant_list = []
    for i in range(len(col1_vals)):
        x = col1_vals[i]
        quant_mask = intersect_not_nan_mask(df, col1, col2, x)
        quant_list.append(df[col2][quant_mask])
        for j in df[quant_mask][col2]:
            n = int(j)
            if n > hmax: hmax = n
            if n < hmin: hmin = n
    if plot_type == 'cols':
        fig, ax = plot_in_cols(quant_list, col1_vals, graph_width,
                                    hmin, hmax, bin_val, htype, title_str)
        make_it_cool(fig, col1_vals, bbox, main_title, mt_size)
        return fig, ax
    elif plot_type == 'style_test':
        pass
    else:
        fig, ax, p = plot_single_axis(quant_list, col1_vals, graph_width,
                                   hmin, hmax, bin_val, htype)
        make_it_cool(fig, col1_vals, bbox, main_title, mt_size)
        return fig, ax
    return
