import re
from io import StringIO
import joypy
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.dates import DateFormatter
import pandas as pd
import datetime


cmap_dict = {'red': ((0.0, 39 / 255, 39 / 255),
                     (1.0, 89 / 255, 89 / 255)),

             'green': ((0.0, 36 / 255, 36 / 255),
                       (1.0, 105 / 255, 105 / 255)),

             'blue': ((0.0, 73 / 255, 73 / 255),
                      (1.0, 255 / 255, 255 / 255))}


def plot_0(ids, dts, id_df):
    avg_prices = [np.mean(id_df[idx]['price_per_msq']) for idx in ids]

    fig, ax = plt.subplots()
    plt.gcf().subplots_adjust(bottom=0.15)
    plt.xlabel("Data scrapping date")
    plt.ylabel("Average price of flat per msq")
    plt.xticks(rotation=45)
    plt.plot(dts, avg_prices, color='#5969FF')
    plt.scatter(dts, avg_prices, color='#0E0C28')
    ax.xaxis.set_major_formatter(DateFormatter('%d.%m.%y'))
    imgdata = StringIO()
    fig.tight_layout()

    ymin, ymax = ax.get_ylim()
    ax.set_ylim(ymin-100, ymax+100)

    ax = plt.gca()
    ax.get_yaxis().get_major_formatter().set_useOffset(False)

    plt.savefig(imgdata, format='svg')
    plt.clf()
    imgdata.seek(0)
    str0 = imgdata.getvalue()
    str0 = re.sub(r"width=\"[^\"]*\"", "width=\"100%\"", str0)

    return str0


def plot_1(ids, dts, id_df):
    new_flats_prop = []

    for idx in ids:
        counts = id_df[idx]['market'].value_counts()
        if 'pierwotny' not in counts:
            counts['pierwotny'] = 0

        if 'wtórny' not in counts:
            counts['wtórny'] = 0
        if counts['pierwotny'] + counts['wtórny'] != 0:
            new_flats_prop.append(counts['pierwotny'] / (counts['pierwotny'] + counts['wtórny']))
        else:
            new_flats_prop.append(0.5)

    used_flats_prop = [1.0 - prop for prop in new_flats_prop]

    fig, ax = plt.subplots()
    plt.xlabel("Data scrapping date")
    plt.ylabel("Proportions of offers types")
    plt.xticks(rotation=45)
    plt.stackplot(dts, new_flats_prop, used_flats_prop, labels=['primary market', 'secondary market'],colors=['#5969FF', '#DDDDDD'])
    ax.xaxis.set_major_formatter(DateFormatter('%d.%m.%y'))
    plt.legend(loc='upper left')
    imgdata = StringIO()
    fig.tight_layout()
    plt.savefig(imgdata, format='svg')
    plt.clf()
    imgdata.seek(0)
    str0 = imgdata.getvalue()
    str0 = re.sub(r"width=\"[^\"]*\"", "width=\"100%\"", str0)

    return str0


def plot_2(ids, dts, id_df):
    categories = [
        ('detached house', 'dom wolnostojący'),
        ('terraced house', 'szeregowiec'),
        ('tenement house', 'kamienica'),
        ('apartment building', 'apartamentowiec'),
        ('residential block', 'blok'),
    ]

    colors = ['#0E0C28', '#1000FF', '#5969FF', '#565659', '#DDDDDD']
    proportions = np.zeros((len(ids), len(categories)))

    for idx_num, idx in enumerate(ids):
        counts = id_df[idx]['building_type'].value_counts()

        for cat_num, category in enumerate(categories):
            if category[1] in counts.keys():
                proportions[idx_num, cat_num] = counts[category[1]]

    proportions += 0.0001
    proportions = proportions / proportions.sum(axis=1)[:, np.newaxis]

    fig, ax = plt.subplots()
    plt.xlabel("Data scrapping date")
    plt.ylabel("Proportions of flat builing types")
    plt.xticks(rotation=45)
    plt.stackplot(dts, proportions.T, labels=[cat[0] for cat in categories], colors=colors)
    ax.xaxis.set_major_formatter(DateFormatter('%d.%m.%y'))
    plt.legend(loc='upper left')
    imgdata = StringIO()
    fig.tight_layout()
    plt.savefig(imgdata, format='svg')
    plt.clf()
    imgdata.seek(0)
    str0 = imgdata.getvalue()
    str0 = re.sub(r"width=\"[^\"]*\"", "width=\"100%\"", str0)

    return str0


def plot_3(ids, dts, id_df):
    df = id_df[ids[-1]].copy()
    df['price'] = df['price'] / 1000
    df = df.loc[df['price'] < 2000]
    counts = df['rooms'].value_counts()
    labels = [key for key in counts.keys() if counts[key] >= 3]
    labels = sorted(labels)
    df = df.loc[df['rooms'].isin(labels)]

    plt.register_cmap(cmap=matplotlib.colors.LinearSegmentedColormap('cmap_custom', cmap_dict))
    fig, axes = joypy.joyplot(df,
                              by="rooms",
                              column="price",
                              labels=labels,
                              range_style='all',
                              grid="y",
                              linewidth=1,
                              legend=False,
                              colormap=plt.get_cmap('cmap_custom'))

    ax = axes[-1]
    ax.yaxis.set_label_position("left")
    ax.yaxis.set_label_coords(-0.06, 0.5)
    ax.yaxis.set_visible(True)
    ax.yaxis.set_ticks([])
    plt.ylabel("Number of rooms in flat")

    locs, labels = plt.xticks()
    plt.xticks(locs, [str(label.get_text()) + 'k zł' for label in labels])
    plt.xticks(rotation=45)
    plt.xlabel("Price for flat")
    plt.subplots_adjust(left=0.1, bottom=0.2)

    imgdata = StringIO()
    plt.savefig(imgdata, format='svg')
    plt.clf()
    imgdata.seek(0)
    str0 = imgdata.getvalue()
    str0 = re.sub(r"width=\"[^\"]*\"", "width=\"100%\"", str0)

    return str0


def plot_4(ids, dts, id_df):
    df = id_df[ids[-1]].copy()
    df = df.loc[df['price'] < 2000000]
    df = df.loc[df['size'].astype(float) < 150]

    x0 = df['size'].astype(float)
    x1 = df['price'].astype(float)/1000.0
    x2 = df['price_per_msq'].astype(float)/1000.0

    slope95 = np.quantile(x2, 0.95)
    slope50 = np.quantile(x2, 0.5)
    slope05 = np.quantile(x2, 0.05)

    line_x = np.arange(np.min(x0), np.max(x0)+1)
    line_95 = slope95 * line_x
    line_50 = slope50 * line_x
    line_05 = slope05 * line_x

    fig, ax = plt.subplots()
    plt.gcf().subplots_adjust(bottom=0.15)
    plt.xlabel("Size of flat")
    plt.ylabel("Price of flat")
    plt.xticks(rotation=45)

    plt.register_cmap(cmap=matplotlib.colors.LinearSegmentedColormap('cmap_custom1', cmap_dict))
    sctr = plt.scatter(x=x0, y=x1, c=x2, s=40, edgecolor='black', linewidth='0.2', cmap='cmap_custom1')
    plt.plot(line_x, line_95, color='black', linestyle=':', linewidth=2.0, label='95% offers < {:.1f}k zł/m²'.format(slope95))
    plt.plot(line_x, line_50, color='black', linestyle='--', linewidth=2.0, label='50% offers < {:.1f}k zł/m²'.format(slope50))
    plt.plot(line_x, line_05, color='black', linestyle='-.', linewidth=2.0, label='95% offers > {:.1f}k zł/m²'.format(slope05))

    plt.legend(loc='upper left')

    plt.ylim(0.0, plt.ylim()[1])
    plt.xlim(0.0, plt.xlim()[1])

    cbar = plt.colorbar(sctr)
    cbar.solids.set_edgecolor("face")
    cbar.solids.set_rasterized(False)

    labels = cbar.ax.get_yticks()
    labels = [str(label) + 'k zł' for label in labels]
    cbar.ax.set_yticklabels(labels)

    plt.tight_layout()
    fig.canvas.draw()

    locs, labels = plt.yticks()
    plt.yticks(locs, [str(label.get_text()) + 'k zł' for label in labels])
    locs, labels = plt.xticks()
    plt.xticks(locs, [str(label.get_text()) + ' m²' for label in labels])

    ax2 = ax.twinx()
    ax2.yaxis.set_label_position("right")
    ax2.set_ylabel("Price of 1m²")
    ax2.yaxis.set_label_coords(1.285, 0.5)
    ax2.yaxis.set_visible(True)
    ax2.yaxis.set_ticks([])

    plt.gcf().subplots_adjust(left=0.15, right=0.95)

    imgdata = StringIO()
    plt.savefig(imgdata, format='svg')
    plt.clf()
    imgdata.seek(0)
    str0 = imgdata.getvalue()
    str0 = re.sub(r"width=\"[^\"]*\"", "width=\"100%\"", str0)

    return str0


def plot_5(ids, dts, id_df):
    dt_for_idx = {ids[i]: dts[i] for i in range(len(ids))}

    dfs = [v.copy() for (k, v) in id_df.items()]
    df = pd.concat(dfs)
    df.reset_index(drop=True, inplace=True)

    df = df.loc[df['price_per_msq'] < 20000]
    df = df.loc[df['price_per_msq'] > 2000]
    df['price_per_msq'] = df['price_per_msq'] / 1000.0

    plt.register_cmap(cmap=matplotlib.colors.LinearSegmentedColormap('cmap_custom', cmap_dict))
    fig, axes = joypy.joyplot(df,
                              by="task_run_id",
                              column="price_per_msq",
                              labels=ids,
                              range_style='all',
                              grid="y",
                              linewidth=1,
                              overlap=2,
                              legend=False,
                              colormap=plt.get_cmap('cmap_custom'))

    ax = axes[-1]
    ax.yaxis.set_label_position("left")
    ax.yaxis.set_label_coords(-0.17, 0.4)
    ax.yaxis.set_visible(True)
    ax.yaxis.set_ticks([])
    plt.ylabel("Data scrapping date")

    for i in range(len(axes)):
        if len(axes[i].get_yticklabels()) == 1:
            label = axes[i].get_yticklabels()[0].get_text()
            axes[i].set_yticklabels([dt_for_idx[label].strftime('%d.%m.%y')])

    locs, labels = plt.xticks()
    plt.xticks(locs, [str(label.get_text()) + 'k zł' for label in labels], rotation=45)
    plt.xlabel("Price for 1m²")
    plt.subplots_adjust(left=0.18, bottom=0.2)

    imgdata = StringIO()
    plt.savefig(imgdata, format='svg')
    plt.clf()
    imgdata.seek(0)
    str0 = imgdata.getvalue()
    str0 = re.sub(r"width=\"[^\"]*\"", "width=\"100%\"", str0)

    return str0