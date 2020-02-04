from pandas import read_csv
import pandas as pd
from tkinter.filedialog import askopenfilename
import tkinter as tk
import os
import plotly.figure_factory as ff

def OpenFile():
    desktop_location = os.path.expanduser("~\Desktop")
    root = tk.Tk()
    root.withdraw()
    name = askopenfilename(initialdir=desktop_location,filetypes =(("Trade Files", "*.csv *.xls *.xlsx *.xlsm"),("All Files","*.*")),title = "Choose a file")
    return name

if __name__ == '__main__':
    file = read_csv('C:\\Users\\yuval\Desktop\\2017_gains.csv')
    file.fillna(0)
    print(file)

    file.rename(columns={'Symbol':'Task', 'Date Acquired':'Start','Date Sold':'Finish','Gain':'Complete'},inplace=True)
    file['Start'] = pd.to_datetime(file.Start)
    file['Finish'] = pd.to_datetime(file.Finish)
    file = file.drop(['Proceeds','Cost Basis','Volume'],1)
    print(file)

    fig = ff.create_gantt(file,title='Trade lifecycle by token',colors=['rgb(114, 44, 121)','rgb(198, 47, 105)','rgb(58, 149, 136)'], show_colorbar=True,bar_width=0.2, showgrid_x=True, showgrid_y=True,
                     group_tasks=True)
    fig.show()
