# -*- mode: python ; coding: utf-8 -*-
import pandas as pd
from functions import OpenFile,prepare_capital_gains_file_for_print,Inflation_Adjusted_Cost_Basis,Convert_to_ILS_Figures,divide_to_different_coins,set_bloxtaxfile,add_info_columns,create_header_footer, create_top_table, create_main_table
import os
import win32com.client
import numpy as np

#before compiling to a file - remember adding these lines to the spec file - after first attemp :
import sys
sys.setrecursionlimit(5000)
#known columns for csv loaded to project:
BitcoinTaxFile_title_identifiers = ['Volume','Symbol','Date Acquired', 'Date Sold', 'Proceeds']
BloxTaxFile_title_identifiers =['רווח\הפסד שקלים (נומינלי)', 'רווח\הפסד שקלים (ריאלי)']
resulotion =''
ComparedProfit = 0

#choose file window:
path = OpenFile()
print(path)
#terminate window midway:
if path == '':
    print('Terminated')
    exit()
#check columns in order to classify origin:
try:
    file = pd.read_excel(path,index_col=False)
    titles = list(file.head(0))
except:
    file = pd.read_csv(path,index_col=False)
    titles = list(file.head(0))
del file

#send to the relevant handling
isbloxtax =  all(elem in titles for elem in BloxTaxFile_title_identifiers)
isbitcointax = all(elem in titles for elem in BitcoinTaxFile_title_identifiers)

capital_gains = pd.DataFrame
if isbitcointax:
    capital_gains = pd.read_csv(path, index_col=None)
elif isbloxtax:
    capital_gains = set_bloxtaxfile(path)
else:
    print('Sorry, your file didnt match any known file we can use')
    exit()
#groupby the page and add info?
relevant_columns = capital_gains.columns.str.find("Unnamed").to_numpy().nonzero()[0]
capital_gains = capital_gains.iloc[:, relevant_columns]
df1 = prepare_capital_gains_file_for_print(capital_gains)

#if necessary, convert USD to ILS
if 'USD' in df1.values:
    print('Original was a USD file')
    df2,resulotion,ComparedProfit = Convert_to_ILS_Figures(df1)
    print(ComparedProfit , ' savings in profits!')
    print('The Calculation was a' , resulotion)
else:
    print('Original was an ILS file')
    df2 = df1
#adjust for inflation:
df3 = Inflation_Adjusted_Cost_Basis(df2) #all capital gains are presented in a singel excel sheet and adjusted to inflation.

df3.index.names = ['עסקה']
#save to regular excel file
where_to_save = path[:-4] + "_edited.xlsx"
writer = pd.ExcelWriter(where_to_save, engine='xlsxwriter', mode='w')
workbook = writer.book
sheet = workbook.add_worksheet()
sheet = workbook.get_worksheet_by_name("Sheet1")
writer.sheets["Sheet1"] = sheet
create_header_footer(sheet, year=df3.loc[0, "תאריך מכירה"].year, length=len(df3) + 13)
create_top_table(df3, writer, sheet)
create_main_table(df3, writer, sheet)
writer.save()
writer.close()
