from functions import divide_to_different_coins
from pandas import read_csv
from tkinter.filedialog import askopenfilename
import tkinter as tk
import os
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import scipy


def OpenFile():
    desktop_location = os.path.expanduser("~\Desktop")
    root = tk.Tk()
    root.withdraw()
    name = askopenfilename(initialdir=desktop_location,filetypes =(("Trade Files", "*.csv *.xls *.xlsx *.xlsm"),("All Files","*.*")),title = "Choose a file")
    return name


path = OpenFile()
print(path)
#terminate window midway:
if path is '':
    print('Terminated')
    exit()
"""
#unique coin - list
file = pd.read_excel(path, index_col=None,encoding='utf-8')
file.fillna('0')
print(file['מטבע'].unique())

#unique coin - hist of each coin
    #read to diff tables
all_coins = divide_to_different_coins(file)
    #filter columns
col = ['תאריך מכירה', 'מחיר מכירה']
d_coin = []
for coin in all_coins:
    d_coin.append(coin[col])
    #work on histogram
"""

series = read_csv(path, header=0, index_col=0, parse_dates=True, squeeze=True)
series.sort_values(ascending= True)
print(series)
series.plot(style='k.')
plt.show()

