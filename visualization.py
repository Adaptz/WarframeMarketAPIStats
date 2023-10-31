#%%
import pandas as pd
import scipy.stats as s
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

items = pd.read_csv("items.csv")

# Converts the 'N.A.' string to Nan so it can be removed if needed with 
# dropna() and so the column can be converted to a float data type
items = items.replace(['N.A.'], [np.nan])

convertDict = {
    'avgPlatMaxed': float,
    'lastSoldMaxed': float,
    'avgPlatDiff': float,
    'lastSoldPlatDiff': float
}
items = items.astype(convertDict)

# Replaces invalid outliers with NaN
items['avgPlatMaxed'] = items['avgPlatMaxed'].where(items['avgPlatMaxed'] < 177.5, np.nan)
items['avgPlat'] = items['avgPlat'].where(items['avgPlat'] < 125, np.nan)

print(f'The shape of the data is {items.shape} \n')

print(items.describe())

#%%
print(items.info())

#%%
sns.kdeplot(data = items, x = 'avgPlat')

#%%
sns.boxplot(data = items, x = 'avgPlat')

#%%
sns.kdeplot(data = items, x = 'avgPlatMaxed')

#%%
sns.boxplot(data = items, x = 'avgPlatMaxed')

#%%
sns.kdeplot(data = items, x = 'avgPlatDiff')

#%%
sns.boxplot(data = items, x = 'avgPlatDiff')
#%%