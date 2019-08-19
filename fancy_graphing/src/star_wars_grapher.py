import pandas as pd
import numpy as np
import os
import sys
sys.path.append(os.environ['SRC_DIR'])
sys.path.append(os.environ['GRAPH_DIR'])
from data_analysis import df_utilities
from star_graph import intersect_not_nan_mask as union_mask
from star_graph import match_hist_color, get_scaled_img
from matplotlib import font_manager as fm
import matplotlib.pyplot as plt
from astropy.visualization import hist
from scipy.stats import norm
from PIL import Image



class StarGraph():
    def __init__(self):
        self.df = self.get_df()
        asset_dir = os.environ['ASSET_DIR']
        fpath = os.path.join(asset_dir,'fonts','starjedi','Starjedi.ttf' )
        self.starjedi = fm.FontProperties(fname=fpath)
        fpath = os.path.join(asset_dir,'fonts','stjelogo','Stjldbl2.ttf')
        self.stjelog = fm.FontProperties(fname=fpath)


    def get_df(self):
        """ Input:
                None
            Output:
                df: Pandas DataFrame - a data frame containing the information
                    stored in the Star Wars API People resources. This data
                    is modified by the cleanup() function in df_utilities.
                    This dataframe is also stored to the computer as
                    dataframe.csv.
        """
        df_path = os.path.join(os.environ['ASSET_DIR'],'dataframe.csv')
        if not os.path.exists(df_path):
            df = df_utilities.build_dataframe()
            df = df_utilities.cleanup(df)
            df.to_csv(df_path)
        else:
            df = pd.read_csv(df_path, index_col = 0)
        return df

    def plot(self, x_col, x_vals, y_col='height', graph_width=10,
                    graph_type='cols', bin_val='freedman', htype='stepfilled',
                    title_str='{}', bbox=[.05,.05,.95,.95], main_title="",
                    mt_size=36, add_norm=True, alpha=.7, save_fig=None,
                    ax_alpha=.1, add_legend=False):
        """ Inputs:
                x_col: string - the name of the column containing the
                    independent variable
                x_vals: list of strings - the names of the values within x_col
                    which we would like to compare
                y_col: string - the name of the column containing the dependent
                    variable
                graph_width: int - the width of the graph in inches
                graph_type: string - the type of graph. 'cols' will plot each
                    item in x_vals on a separate suplot, with the subplots
                    arranged in two columns. 'single' will plot all the items
                    in x_vals on a single axes.
                bin_val: string - the name of the bin algorithm to use
                htype: string - the histogram type
                title_str: string - a string which will be made into the title
                    in the following way:
                            title_str.format("value contained in x_vals")
                    With the current setup, the unmodified x_val entry will be
                    displayed.
                bbox: sequence - this will be treated as a matplotlib boundary
                    box for the purposes of setting the position for the
                    background image
                main_title: string - the title of the entire figure
                mt_size: int or string - the size of the main title text.
                add_norm: whether a normal distribution should be fitted to the
                    data and plotted over each axes.
                alpha: float - the alpha value to apply to histograms
                save_fig: string - the name to save the figure as
                ax_alpha: float - the alpha value to apply to the axes
            Output:
                ax: matplotlib axes
                fig: matplotlib figure
                Also saves a figure to the image directory if save_fig is given.
        """
        self.x_vals = x_vals
        self.x_col = x_col
        self.y_col = y_col
        self.graph_width = graph_width
        self.graph_type = graph_type
        self.bin_val = bin_val
        self.htype = htype
        self.quant_list = []
        self.title_str = title_str
        self.bbox = bbox
        self.main_title = main_title
        self.mt_size=mt_size
        self.add_norm = add_norm
        self.alpha = alpha
        self.ax_alpha=ax_alpha
        self.hmax = self.df[y_col].max()
        self.hmin = self.df[y_col].min()
        self.add_legend=add_legend
        for x in x_vals:
            quant_mask = union_mask(self.df, x_col, y_col, x)
            self.quant_list.append(self.df[y_col][quant_mask])
        if graph_type == 'cols':
            self.fig, ax = self.plot_cols()
        if graph_type == 'single':
            self.fig, ax = self.plot_single()
            self.fig = self.make_it_cool()
        else:
            pass
        if save_fig:
            fig_path=os.path.join((os.environ['ASSET_DIR'],'images',save_fig))
            fig.savefig()
        return self.fig, ax

    def plot_cols(self):
        """
        Plots histograms for x_vals in two columns
        """
        self.ax_list = []
        self.plot_height = xlen // 2 + xlen % 2
        self.fig = plt.figure(figsize=(graph_width, \
                                        self.plot_height*(self.graph_width/2)))
        img = get_scaled_img(self.fig)
        ax_im = plt.imshow(img)
        plt.axis('off')
        for y, c, i in zip(self.quant_list,self.x_vals,range(len(self.x_vals))):
            if len(ax_list)==0:
                ax = self.fig.add_subplot(plot_height,2, i+1, alpha=0)
            else:
                ax = self.fig.add_subplot(plot_height,2,i+1, alpha=0, \
                                    sharex=ax_list[0],sharey=ax_list[0])
        self.ax_list.append(ax)
        ax = self._hist(y, ax, c)
        ax = self._plot_norm(y, ax)
        self.fig = self.make_it_cool()
        return self.fig, ax

    def plot_single(self):
        """
        Plots histograms for x_vals on a single axes
        """
        self.fig, ay = plt.subplots(figsize=(self.graph_width,self.graph_width))
        img = get_scaled_img(self.fig)
        ay.imshow(img)
        ay.axis('off')
        ax = self.fig.add_subplot(111)
        for y, c, i in zip(self.quant_list,self.x_vals,range(len(self.x_vals))):
            ax = self._hist(y, ax, c)
            ax = self._plot_norm(y, ax)
            ax = self.axis_style(ax,"", alpha=0)
            ax.tick_params('both',labelsize=16)
        if self.add_legend:
            plt.legend(loc='upper right',prop=self.starjedi, \
                        bbox_to_anchor=[1,.95])
        return self.fig, ax

    def _hist(self, y, ax, label):
        n, bins, patches = hist(y, bins=self.bin_val, ax=ax,
                                histtype=self.htype, alpha=self.alpha,
                                density=True, label=label)
        return ax

    def _plot_norm(self, y, ax):
        mu, std = norm.fit(y)
        x = np.linspace(self.hmin, self.hmax, 100)
        y = norm.pdf(x, mu, std)
        c = match_hist_color(self.fig)
        l = ax.plot(x, y, color=c, linewidth=3, alpha=1)
        return ax

    def make_it_cool(self):
        self.fig.get_children()[1].axis("off")
        self.fig.get_children()[1].set_position(self.bbox)
        if len(self.fig.get_children()) > 3:
            for i, title in zip(self.fig.get_children()[2:], self.x_vals):
                i = self.axis_style(i,title)
        else:
            pass
        self.fig.suptitle(self.main_title,fontproperties=self.stjelog,
                     color='#FFE81F', fontsize=self.mt_size)
        return self.fig

    def axis_style(self,ax,title,alpha=.1):
        ax.patch.set_facecolor((1, 1, 1, alpha))
        ax.patch.set_linewidth(2)
        ax.tick_params(axis='both', colors='white')
        ax.set_title(title, fontproperties=self.starjedi,
                        color='white', size='xx-large')
        ax.spines['left'].set_color('white')
        ax.spines['bottom'].set_color('white')
        return ax
