import data
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from bisect import bisect_right
from scipy.stats import norm
from matplotlib.ticker import MultipleLocator
from importlib import resources as impresources


HEIGHT_PATH = (impresources.files(data) / 'height_data.csv')
WEIGHT_PATH = (impresources.files(data) / 'weight_data.csv')
PARA_PATH = (impresources.files(data) / 'para.csv')

quantiles = [
    0.002,
    0.005,
    0.010,
    0.020,
    0.030,
    0.050,
    0.070,
    0.100,
    0.150,
    0.200,
    0.300,
    0.400,
    0.500,
    0.600,
    0.700,
    0.800,
    0.850,
    0.900,
    0.930,
    0.950,
    0.970,
    0.980,
    0.990,
    0.995,
    0.998
]


def height_score(sex: str, age: int, height: int) -> float:
    """Function that calculates the height score for a user.

    Parameters
    ----------
    sex : str
        Sex of the subject. Male ('male') or female ('female').
    age : int
        Age of the subject in years.
    height : int
        Height of the subject in cm.

    Returns
    -------
    float
        Height score
    """
    height = height/100
    height_data = pd.read_csv(HEIGHT_PATH).set_index(['male', 'age'])
    is_male = int(sex.lower() == 'male')

    height_range = height_data.loc[(is_male, age), :].values
    index = min(max(1, bisect_right(height_range, height)), len(quantiles)-1)

    x1 = height_range[index-1]
    q1 = quantiles[index-1]
    x2 = height_range[index]
    q2 = quantiles[index]

    y1 = norm.ppf(q1)
    y2 = norm.ppf(q2)
    a = (y2-y1)/(x2-x1)
    b = y1-a*x1

    out = norm.cdf(a*height+b)*100

    if (height < min(height_range)*0.9):
        out = 0
    elif (height > max(height_range)*1.2):
        out = 100

    return out


def weight_score(sex: str, age: int, weight: float) -> float:
    """Function that calculates the weight score for a user.

    Parameters
    ----------
    sex : str
        Sex of the subject. Male ('male') or female ('female').
    age : int
        Age of the subject in years.
    weight : int
        weight of the subject in kg.

    Returns
    -------
    float
        Weight score
    """
    weight_data = pd.read_csv(WEIGHT_PATH).set_index(['male', 'age'])
    is_male = int(sex.lower() == 'male')

    weight_range = weight_data.loc[(is_male, age), :].values
    index = min(max(1, bisect_right(weight_range, weight)), len(quantiles)-1)

    x1 = np.log(weight_range[index-1])
    q1 = quantiles[index-1]
    x2 = np.log(weight_range[index])
    q2 = quantiles[index]

    y1 = norm.ppf(q1)
    y2 = norm.ppf(q2)
    a = (y2-y1)/(x2-x1)
    b = y1-a*x1

    out = norm.cdf(a*np.log(weight)+b)*100

    if (weight < min(weight_range)*0.9):
        out = 0
    elif (weight > max(weight_range)*1.2):
        out = 100

    return out


def height_range(sex: str, age: int) -> tuple:
    """Function that returns the minimum and maximum
    of the height.

    Parameters
    ----------
    sex : str
        Sex of the subject. Male ('male') or female ('female').
    age : int
        Age of the subject in years.

    Returns
    -------
    tuple
        Tuple with minimum and maximum values
    """
    height_data = pd.read_csv(HEIGHT_PATH).set_index(['male', 'age'])
    is_male = int(sex.lower() == 'male')
    height_range = height_data.loc[(is_male, age), :].values

    return (min(height_range)*100, max(height_range)*100)


def weight_range(sex: str, age: int) -> tuple:
    """Function that returns the minimum and maximum
    of the weight.

    Parameters
    ----------
    sex : str
        Sex of the subject. Male ('male') or female ('female').
    age : int
        Age of the subject in years.

    Returns
    -------
    tuple
        Tuple with minimum and maximum values
    """
    weight_data = pd.read_csv(WEIGHT_PATH).set_index(['male', 'age'])
    is_male = int(sex.lower() == 'male')
    weight_range = weight_data.loc[(is_male, age), :].values

    return (min(weight_range), max(weight_range))


def haw_score(sex: str, age: int, height: int, weight: float) -> float:
    """Function that calculates the Height-adjusted weight (HaW) score
      for a user.

    Parameters
    ----------
    sex : str
        Sex of the subject. Male ('male') or female ('female').
    age : int
        Age of the subject in years.
    height : int
        weight of the subject in kg.
    weight : int
        weight of the subject in kg.

    Returns
    -------
    float
        Height-adjusted Weight score
    """
    height = height/100
    para_data = pd.read_csv(PARA_PATH).set_index(['male', 'age'])
    is_male = int(sex.lower() == 'male')

    para = para_data.loc[(is_male, age), :].sort_values(by='q')
    para['wt'] = para.c0+para.c1*height+para.c2*height**2+para.c3*height**3

    index = min(max(1, bisect_right(para.wt.values, weight)), len(para)-1)

    x1 = np.log(para.wt.values[index-1])
    q1 = para.q.values[index-1]
    x2 = np.log(para.wt.values[index])
    q2 = para.q.values[index]

    y1 = norm.ppf(q1)
    y2 = norm.ppf(q2)
    a = (y2-y1)/(x2-x1)
    b = y1-a*x1

    out = norm.cdf(a*np.log(weight)+b)*100

    if (weight < para.wt.min()*0.9):
        out = 0
    elif (weight > para.wt.max()*1.2):
        out = 100

    return out


def get_coefficients(sex: str, age: int, q: float) -> tuple:
    """Function that returns the coefficients for the polynomial of the
     quantile of the specified age and sex closest in the data.

    Parameters
    ----------
    sex : str
        Sex of the subject. Male ('male') or female ('female').
    age : int
        Age of the subject in years.
    q : float
        Quantile.

    Returns
    -------
    tuple
        Tuple with the coefficients
        (quantile, intercept, order 1, order 2, order 3).
    """
    para_data = pd.read_csv(PARA_PATH).set_index(['male', 'age'])
    is_male = int(sex.lower() == 'male')

    para = para_data.loc[(is_male, age), :].sort_values(by='q')
    para = para[(para.q >= q) & (para.q < q*1.1)].iloc[0, :]

    return ((para.q, para.c0, para.c1, para.c2, para.c3))


def get_height_and_weight_plot(
        sex: str, age: int, height: int, weight: float, **args
        ) -> float:
    """Function that plots the height and weight percentiles.

    Parameters
    ----------
    sex : str
        Sex of the subject. Male ('male') or female ('female').
    age : int
        Age of the subject in years.
    height : int
        weight of the subject in kg.
    weight : int
        weight of the subject in kg.
    args:
        Parameters to be passed to matplotlib figure.

    Returns
    -------
    plt.Figure
        Figure with the plot
    """
    h_score = height_score(sex, age, height)
    w_score = weight_score(sex, age, weight)

    h_min, h_max = height_range(sex, age)
    w_min, w_max = weight_range(sex, age)

    fig, ax = plt.subplots(1, subplot_kw=dict(box_aspect=1), **args)
    ax.set_title(f'Height and Weight Percentiles in {age} yrs-old {sex}')
    ax.set_xlim(h_min, h_max)
    ax.set_ylim(w_min, w_max)
    ax.set_xlabel('Height [cm]')
    ax.set_ylabel('Weight [kg]')
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.xaxis.set_major_locator(MultipleLocator(10))

    is_male = int(sex.lower() == 'male')
    weight_data = pd.read_csv(WEIGHT_PATH).set_index(['male', 'age'])
    height_data = pd.read_csv(HEIGHT_PATH).set_index(['male', 'age'])

    w_range = weight_data.loc[(is_male, age), :].values
    h_range = height_data.loc[(is_male, age), :].values

    ax.axvspan(
        min(h_range)*100,
        max(h_range)*100,
        (min(w_range)-w_min)/(w_max-w_min),
        (max(w_range)-w_min)/(w_max-w_min),
        facecolor='mistyrose'
    )
    ax.axvspan(
        h_range[3]*100,
        h_range[21]*100,
        (w_range[3]-w_min)/(w_max-w_min),
        (w_range[21]-w_min)/(w_max-w_min),
        facecolor='lightyellow'
    )
    ax.axvspan(
        h_range[7]*100,
        h_range[17]*100,
        (w_range[7]-w_min)/(w_max-w_min),
        (w_range[17]-w_min)/(w_max-w_min),
        facecolor='greenyellow'
    )

    ax.hlines(weight, h_min, h_max, colors='lightcoral', linestyle='--')
    ax.vlines(height, w_min, w_max, colors='lightcoral', linestyle='--')
    ax.scatter([height], [weight], marker='D', color='lightcoral')

    if (height < h_min or height > h_max):
        ax.text(
            h_max,
            (w_min+w_max)/2,
            "Height not in the assessable range!",
            c='lightcoral'
            )
    else:
        ax.text(
            height,
            w_min+(w_max-w_min)/30,
            f"{h_score: .1f}%",
            c='lightcoral',
            fontsize=17
            )
    if (weight < w_min or weight > w_max):
        ax.text(
            (h_min+h_max)/2,
            w_max,
            "Weight not in the assessable range!",
            c='lightcoral'
            )
    else:
        ax.text(
            h_min,
            weight+(w_max-w_min)/30,
            f"{w_score: .1f}%",
            c='lightcoral',
            fontsize=17
            )

    fig.tight_layout()

    return fig


def get_haw_plot(
        sex: str, age: int, height: int, weight: float, **args
        ) -> float:
    """Function that plots the height-adjusted weight percentiles.

    Parameters
    ----------
    sex : str
        Sex of the subject. Male ('male') or female ('female').
    age : int
        Age of the subject in years.
    height : int
        weight of the subject in kg.
    weight : int
        weight of the subject in kg.
    args:
        Parameters to be passed to matplotlib figure.

    Returns
    -------
    plt.Figure
        Figure with the plot
    """
    hw_score = haw_score(sex, age, height, weight)

    h_min, h_max = height_range(sex, age)
    w_min, w_max = weight_range(sex, age)

    fig, ax = plt.subplots(1, subplot_kw=dict(box_aspect=1), **args)
    ax.set_title(f'Height-adjusted Weight Percentile in {age} yrs-old {sex}')
    ax.set_xlim(h_min, h_max)
    ax.set_ylim(w_min, w_max)
    ax.set_xlabel('Height [cm]')
    ax.set_ylabel('Weight [kg]')
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.xaxis.set_major_locator(MultipleLocator(10))

    x = np.linspace(h_min, h_max, 50)
    c = get_coefficients(sex, age, 0.1)
    y_10 = c[1]+c[2]*(x/100)+c[3]*(x/100)**2+c[4]*(x/100)**3
    c = get_coefficients(sex, age, 0.9)
    y_90 = c[1]+c[2]*(x/100)+c[3]*(x/100)**2+c[4]*(x/100)**3
    c = get_coefficients(sex, age, 0.02)
    y_2 = c[1]+c[2]*(x/100)+c[3]*(x/100)**2+c[4]*(x/100)**3
    c = get_coefficients(sex, age, 0.98)
    y_98 = c[1]+c[2]*(x/100)+c[3]*(x/100)**2+c[4]*(x/100)**3

    ax.fill_between(x, y_98, np.zeros_like(x)+w_max, color='mistyrose')
    ax.fill_between(x, np.zeros_like(x)+w_min, y_2, color='mistyrose')
    ax.fill_between(x, y_2, y_98, color='lightyellow')
    ax.fill_between(x, y_10, y_90, color='greenyellow')

    ax.hlines(weight, h_min, h_max, colors='lightcoral', linestyle='--')
    ax.vlines(height, w_min, w_max, colors='lightcoral', linestyle='--')
    ax.scatter([height], [weight], marker='D', color='lightcoral')

    ax.text(
        height,
        weight+(w_max-w_min)/30,
        f"{hw_score: .1f}%",
        c='lightcoral',
        fontsize=17
        )

    return fig


def get_plots(
        sex: str,
        age: int,
        height: int,
        weight: float,
        horizontal: bool = False,
        **args
        ) -> float:
    """Function that plots the height-adjusted weight percentiles and
    the height and weight percentiles.

    Parameters
    ----------
    sex : str
        Sex of the subject. Male ('male') or female ('female').
    age : int
        Age of the subject in years.
    height : int
        Height of the subject in cm.
    weight : int
        Weight of the subject in kg.
    horizontal : bool, optional
        Whether to plot the plots side by side (True) or
        vertically stacked (False). Default: False.
    args:
        Parameters to be passed to matplotlib figure.

    Returns
    -------
    plt.Figure
        Figure with the plot
    """
    columns = [
        "Sex", "Age", "Height", "Weight",
        "H. percentile", "W. percentile", "HaW"
        ]
    val = [[sex,
            f'{age} Yrs',
            f'{height}cm',
            f'{weight}kg',
            f'{height_score(sex, age, height):.1f}%',
            f'{weight_score(sex, age, weight):.1f}%',
            f'{haw_score(sex, age, height, weight):.1f}%']]
    df = pd.DataFrame(val, columns=columns)

    h_score = height_score(sex, age, height)
    w_score = weight_score(sex, age, weight)
    hw_score = haw_score(sex, age, height, weight)

    h_min, h_max = height_range(sex, age)
    w_min, w_max = weight_range(sex, age)

    fig, (ax0, ax, ax2) = plt.subplots(
        2+(horizontal is False)*1,
        1+(horizontal is True)*1,
        **args)

    ax0.axis('tight')
    ax0.axis('off')
    ax0.table(
        cellText=df.values,
        colLabels=df.columns,
        loc='center'
        )

    ax.set_title(f'Height and Weight Percentiles in {age} yrs-old {sex}')
    ax.set_xlim(h_min, h_max)
    ax.set_ylim(w_min, w_max)
    ax.set_xlabel('Height [cm]')
    ax.set_ylabel('Weight [kg]')
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.xaxis.set_major_locator(MultipleLocator(10))

    is_male = int(sex.lower() == 'male')
    weight_data = pd.read_csv(WEIGHT_PATH).set_index(['male', 'age'])
    height_data = pd.read_csv(HEIGHT_PATH).set_index(['male', 'age'])

    w_range = weight_data.loc[(is_male, age), :].values
    h_range = height_data.loc[(is_male, age), :].values

    ax.axvspan(
        min(h_range)*100,
        max(h_range)*100,
        (min(w_range)-w_min)/(w_max-w_min),
        (max(w_range)-w_min)/(w_max-w_min),
        facecolor='mistyrose'
    )
    ax.axvspan(
        h_range[3]*100,
        h_range[21]*100,
        (w_range[3]-w_min)/(w_max-w_min),
        (w_range[21]-w_min)/(w_max-w_min),
        facecolor='lightyellow'
    )
    ax.axvspan(
        h_range[7]*100,
        h_range[17]*100,
        (w_range[7]-w_min)/(w_max-w_min),
        (w_range[17]-w_min)/(w_max-w_min),
        facecolor='greenyellow'
    )

    ax.hlines(weight, h_min, h_max, colors='lightcoral', linestyle='--')
    ax.vlines(height, w_min, w_max, colors='lightcoral', linestyle='--')
    ax.scatter([height], [weight], marker='D', color='lightcoral')

    if (height < h_min or height > h_max):
        ax.text(
            h_max,
            (w_min+w_max)/2,
            "Height not in the assessable range!",
            c='lightcoral'
            )
    else:
        ax.text(
            height,
            w_min+(w_max-w_min)/30,
            f"{h_score: .1f}%",
            c='lightcoral',
            fontsize=17
            )
    if (weight < w_min or weight > w_max):
        ax.text(
            (h_min+h_max)/2,
            w_max,
            "Weight not in the assessable range!",
            c='lightcoral'
            )
    else:
        ax.text(
            h_min,
            weight+(w_max-w_min)/30,
            f"{w_score: .1f}%",
            c='lightcoral',
            fontsize=17
            )

    ax2.set_title(f'Height-adjusted Weight Percentile in {age} yrs-old {sex}')
    ax2.set_xlim(h_min, h_max)
    ax2.set_ylim(w_min, w_max)
    ax2.set_xlabel('Height [cm]')
    ax2.set_ylabel('Weight [kg]')
    ax2.yaxis.set_major_locator(MultipleLocator(10))
    ax2.xaxis.set_major_locator(MultipleLocator(10))

    x = np.linspace(h_min, h_max, 50)
    c = get_coefficients(sex, age, 0.1)
    y_10 = c[1]+c[2]*(x/100)+c[3]*(x/100)**2+c[4]*(x/100)**3
    c = get_coefficients(sex, age, 0.9)
    y_90 = c[1]+c[2]*(x/100)+c[3]*(x/100)**2+c[4]*(x/100)**3
    c = get_coefficients(sex, age, 0.02)
    y_2 = c[1]+c[2]*(x/100)+c[3]*(x/100)**2+c[4]*(x/100)**3
    c = get_coefficients(sex, age, 0.98)
    y_98 = c[1]+c[2]*(x/100)+c[3]*(x/100)**2+c[4]*(x/100)**3

    ax2.fill_between(x, y_98, np.zeros_like(x)+w_max, color='mistyrose')
    ax2.fill_between(x, np.zeros_like(x)+w_min, y_2, color='mistyrose')
    ax2.fill_between(x, y_2, y_98, color='lightyellow')
    ax2.fill_between(x, y_10, y_90, color='greenyellow')

    ax2.hlines(weight, h_min, h_max, colors='lightcoral', linestyle='--')
    ax2.vlines(height, w_min, w_max, colors='lightcoral', linestyle='--')
    ax2.scatter([height], [weight], marker='D', color='lightcoral')

    ax2.text(
        height,
        weight+(w_max-w_min)/30,
        f"{hw_score: .1f}%",
        c='lightcoral',
        fontsize=17
        )

    ax.set_box_aspect(1)
    ax2.set_box_aspect(1)
    fig.tight_layout()

    return fig
