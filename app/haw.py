import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from bisect import bisect_right
from scipy.stats import norm
import pathlib

cwd = str(pathlib.Path(__file__).parent)
HEIGHT_PATH = f"{cwd}/../data/height_data.csv"
WEIGHT_PATH = f"{cwd}/../data/weight_data.csv"
PARA_PATH = f"{cwd}/../data/para.csv"

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

    return (min(weight_range)*100, max(weight_range)*100)


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