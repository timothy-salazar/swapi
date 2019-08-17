import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from PIL import Image
from astropy.visualization import hist
from scipy.stats import norm

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

def match_hist_color(fig):
    p_list = [i for i in fig.axes[-1].get_children()
         if type(i) == matplotlib.patches.Polygon]
    return p_list[-1].get_facecolor()

def get_scaled_img(fig):
    fig_size = fig.get_size_inches()*fig.dpi
    img = Image.open('assets/images/starfield.png')
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
        ax_list.append(fig.add_subplot(plot_height,2,i+1, alpha=0))
        n, bins, patches = hist(v1, bins=bin_val, ax=ax_list[-1],
                                histtype=htype, alpha=0.7, density=True)
        mu, std = norm.fit(v1)
        x = np.linspace(hmin, hmax, 100)
        y = norm.pdf(x, mu, std)
        c = match_hist_color(fig)
        l = ax_list[-1].plot(x, y, color=c, linewidth=3, alpha=1)
        ax_list[-1].set_title(title_str.format(col1_vals[i]))
    return fig, ax_list
