# -*- mode: python ; coding: utf-8 -*-
import pandas as pd
import dateutil
from tkinter.filedialog import askopenfilename
import tkinter as tk
import os
import pathlib
import datetime
import requests


def divide_to_different_coins(pd1):
    coins = pd1['מטבע'].unique()
    pd_list = []
    for i in coins:
        condition = (pd1['מטבע']== i)
        df2 = pd1[condition]
        df2.reset_index( drop=True, inplace = True)
        pd_list.append(df2)
    return pd_list

def apply_with_exchange_rate_profit_loss(file):
    # convert from USD to ILS
    Dollar_ILS_Rates = pd.read_excel('../dollar values.xlsx', index_col=None)
    Last_known_Rate = Dollar_ILS_Rates['USD/ILS'].tail(1).values[0]
    file.columns = ["Symbol", "Volume", "Date Acquired", "Date Sold",'Buy Price','Sell Price','marginal_percent', "Currency", "Proceeds", "Nominal_Cost_Basis",
                    "Gain"]

    # change caption of currency to ILS
    file['Currency'] = 'ILS'
    # left merge for purchasings USD rate
    file.rename(columns={'Date Acquired': 'Date'}, inplace=True)
    result = file.merge(Dollar_ILS_Rates, on='Date', how='left')
    result['USD/ILS'].fillna(0, inplace=True)
    result.loc[result['USD/ILS'] == 0, 'USD/ILS'] = Last_known_Rate

    # update ILS value for cost_base, delete "Dollar_ILS_Rates" column, rename 'Date' to 'Date Acquired'
    result['Nominal_Cost_Basis'] *= result['USD/ILS']
    result['Buy Price'] *= result['USD/ILS']
    result['Nominal_Cost_Basis'] = round(result['Nominal_Cost_Basis'], 2)
    del result['USD/ILS']
    result.rename(columns={'Date': 'Date Acquired'}, inplace=True)

    # left merge for sales USD rate
    result.rename(columns={'Date Sold': 'Date'}, inplace=True)
    result2 = result.merge(Dollar_ILS_Rates, on='Date', how='left')
    result2['USD/ILS'].fillna(0, inplace=True)
    result2.loc[result2['USD/ILS'] == 0, 'USD/ILS'] = Last_known_Rate

    # update ILS value for Proceeds, delete "Dollar_ILS_Rates" column, rename 'Date' to 'Date Sold'
    result2['Proceeds'] *= result2['USD/ILS']
    result2['Sell Price'] *= result2['USD/ILS']
    result2['Proceeds'] = round(result2['Proceeds'], 2)
    del result2['USD/ILS']
    result2.rename(columns={'Date': 'Date Sold'}, inplace=True)

    # update gains column
    result2['Gain'] = result2['Proceeds'] - result2['Nominal_Cost_Basis']
    return result2

def apply_none_exchange_rate_profit_loss(file):
    Dollar_ILS_Rates = pd.read_excel('../dollar values.xlsx', index_col=None)
    Last_known_Rate = Dollar_ILS_Rates['USD/ILS'].tail(1).values[0]
    file.columns = ["Symbol", "Volume", "Date Acquired", "Date Sold",'Buy Price','Sell Price','marginal_percent', "Currency", "Proceeds", "Nominal_Cost_Basis",
                    "Gain"]

    # change caption of currency to ILS
    file['Currency'] = 'ILS'
    # left merge for purchasings USD rate
    file.rename(columns={'Date Sold': 'Date'}, inplace=True)
    result = file.merge(Dollar_ILS_Rates, on='Date', how='left')
    result['USD/ILS'].fillna(0, inplace=True)
    result.loc[result['USD/ILS'] == 0, 'USD/ILS'] = Last_known_Rate

    # update ILS value for cost_base, delete "Dollar_ILS_Rates" column, rename 'Date' to 'Date Acquired'
    result['Nominal_Cost_Basis'] *= result['USD/ILS']
    result['Nominal_Cost_Basis'] = round(result['Nominal_Cost_Basis'], 2)
    result['Proceeds'] *= result['USD/ILS']
    result['Proceeds'] = round(result['Proceeds'], 2)
    result['Buy Price'] *= result['USD/ILS']
    result['Sell Price'] *= result['USD/ILS']

    del result['USD/ILS']
    result.rename(columns={'Date': 'Date Sold'}, inplace=True)

    # update gains column
    result['Gain'] = result['Proceeds'] - result['Nominal_Cost_Basis']
    return result

def Convert_to_ILS_Figures(file : pd.DataFrame):
    no_exchange_diff = apply_none_exchange_rate_profit_loss(file)
    with_exchange_diff = apply_with_exchange_rate_profit_loss(file)
    preferred = pd.DataFrame
    resulotion = ''
    ComparedProfit = no_exchange_diff['Gain'].sum() - with_exchange_diff['Gain'].sum()
    if ComparedProfit < 0 :
        preferred = no_exchange_diff
        resulotion = "ILS Calculation"
    else:
        preferred = with_exchange_diff
        resulotion = "USD Calculation"

    return preferred,resulotion,ComparedProfit


def _add_missing_rates(current_rates, num):
    api_url = 'https://api.cbs.gov.il/index/data/price'
    options = {'id':'120010', 'format': 'json', 'download': 'false', 'coef': 'true'}
    options['last'] = num
    rates = requests.get(api_url, options).json()
    new_df_rows = []
    for rate in rates['month'][0]['date']:
        year = rate['year']
        month = rate['month']
        val = rate['prevBase'][-1]['value']
        new_df_rows.append(pd.DataFrame({'YearMonth': year * 100 + month, 'Rate': val}, index=[0]))
    new_df = pd.concat(reversed(new_df_rows), ignore_index=True)
    current_rates = current_rates.append(new_df)
    current_rates.to_excel('rates.xlsx', index=False)
    return current_rates


def get_updated_rates():
    current_rates = pd.read_excel('rates.xlsx', index_col=None)
    current_date = datetime.datetime.now()
    last_rate_date = int(current_rates.iloc[-1, 0])
    year, month = divmod(last_rate_date, 100)
    last_as_date = datetime.datetime(year, month, 1)
    num_missing = (current_date.year - last_as_date.year) * 12 + (current_date.month - last_as_date.month)
    if num_missing > 1:
        current_rates = _add_missing_rates(current_rates, num_missing - 1)
    return current_rates


def Inflation_Adjusted_Cost_Basis(file: pd.DataFrame):
    Israeli_Rates = get_updated_rates()
    Last_known_Rate = Israeli_Rates['Rate'].tail(1).values[0]

    test_file = file
    test_file.columns = ["Symbol","Volume","Date Acquired","Date Sold",'Buy Price','Sell Price','marginal_percent',"Currency","Proceeds","Nominal_Cost_Basis","Gain"]

    #add Purchased YearMonth value to the list
    test_file['YearMonth'] = test_file['Date Acquired'].map(lambda x: 100*x.year + x.month)
    results=test_file.merge(Israeli_Rates,on='YearMonth',how = 'left')
    results['Rate'].fillna(0,inplace = True)
    results.loc[results['Rate'] == 0 , 'Rate'] = Last_known_Rate

    results.rename(columns = {'Rate':'Purchasing_rate'}, inplace = True)

    del results['YearMonth']

    #add Sale YearMonth value to the list
    results['YearMonth'] = results['Date Sold'].map(lambda x: 100*x.year + x.month)
    results2=results.merge(Israeli_Rates,on='YearMonth',how = 'left')
    results2['Rate'].fillna(0, inplace=True)
    results2.loc[results2['Rate'] == 0, 'Rate'] = Last_known_Rate

    results2.rename(columns = {'Rate':'Sale_rate'}, inplace = True)

    del results2['YearMonth']

    #add inflation percentage
    results2['Periodical_Inflation_In_percent'] = round(((results2['Sale_rate']/results2['Purchasing_rate'])-1)*100,3)

    #add inflation adjustment to cost basis
    results2['Inflation_Adjusted_Cost_Basis'] =  results2.Nominal_Cost_Basis * (1+(results2.Periodical_Inflation_In_percent/100))
    results2['Periodical_Inflation'] = results2['Inflation_Adjusted_Cost_Basis'] - results2['Nominal_Cost_Basis']
    results2.loc[results2['Periodical_Inflation'] < 0, 'Inflation_Adjusted_Cost_Basis'] = results2['Nominal_Cost_Basis']
    results2.loc[results2['Periodical_Inflation'] < 0,'Periodical_Inflation'] = 0


    #calculate two types of variances for profit/gains
    results2['nominal_gain'] = results2['Proceeds'] - results2['Nominal_Cost_Basis']
    results2['adjusted_gain'] = results2['Proceeds'] - results2['Inflation_Adjusted_Cost_Basis']

    #pick the correct gain method
    #adjusted gain = proper gain
    results2.loc[results2.adjusted_gain > 0 ,'Gain'] = results2['adjusted_gain']
    #nominal gain is negetive = nominal loss
    results2.loc[results2.nominal_gain < 0,'Gain'] = results2['nominal_gain']
    #adjusted gain is negetive, nominal gain is positive:
    results2.loc[(results2.adjusted_gain < 0) & (results2.nominal_gain > 0) , 'Gain'] = 0

    #results2['Gain'] = results['Proceeds'] - results2['Inflation_Adjusted_Cost_Basis']
    cols = ['Symbol'] + ['Volume'] + ['Date Acquired'] + ['Date Sold'] + ['Buy Price'] + ['Sell Price'] + ['marginal_percent'] + ['Purchasing_rate'] + ['Sale_rate'] +\
           ['Proceeds'] + ['Nominal_Cost_Basis'] + ['Periodical_Inflation'] + ['Inflation_Adjusted_Cost_Basis'] +['nominal_gain'] + ['adjusted_gain'] + ['Gain']
    results2 = results2[cols]

    #fix date variable to look better
    try:
        results2['Date Acquired'] = results2['Date Acquired'].dt.date
        results2['Date Sold'] = results2['Date Sold'].dt.date
    except:
        pass

    #give hebrew titles
    results2.columns = ["מטבע","כמות","תאריך רכישה","תאריך מכירה","מחיר קניה","מחיר מכירה","רווח-הפסד שולי באחוזים","מדד רכישה (לפי בסיס 51)",
                        "מדד מכירה (לפי בסיס 51)","תמורה בשקלים-שוי עסקת ברטר","עלות מקורית נומינאלית","סכום אינפלציוני","עלות מקורית מתואמת","רווח/הפסד נומינאלי","רווח-הפסד ריאלי","רווח-הפסד לצורכי מס"]

    return results2

def add_info_columns(df):

    return df

def prepare_capital_gains_file_for_print(df1):
    ## in case "Date Sold" and "Date Acquired" is with chars such as "-" between parameters, these two lines of code will fix
    try:
        df1['Date Sold'] = df1['Date Sold'].apply(dateutil.parser.parse, dayfirst=False)
        df1['Date Acquired'] = df1['Date Acquired'].apply(dateutil.parser.parse, dayfirst=False)
    except:
        pass

    #delete unmatched coloumn if exists
    if 'Unmatched' in list(df1.head(0)):
        df1.drop(['Unmatched'],axis =1 ,inplace = True)

    #groupby rows by condition
    x = df1.groupby(['Date Sold','Date Acquired','Symbol','Currency'], as_index=False).sum()
    x['Buy Price'] = x['Cost Basis'] / x['Volume']
    x['Sell Price'] = x['Proceeds'] / x['Volume']
    x['marginal_percent'] =  round(((x['Sell Price'] / x['Buy Price']) -1),3)
    print(x)

    cols = ['Symbol','Volume','Date Acquired','Date Sold','Buy Price','Sell Price','marginal_percent','Currency','Proceeds','Cost Basis','Gain']
    x = x[cols]
    x = x.sort_values(by=['Symbol','Date Sold'],ascending=True)
    x.columns =["מטבע","כמות","תאריך רכישה","תאריך מכירה","מחיר קניה","מחיר מכירה","רווח-הפסד שולי באחוזים","מטבע הצגה","תמורה","עלות מקורית","רווח-הפסד"]

    return x

def OpenFile():
    desktop_location = os.path.expanduser("~\Desktop")
    root = tk.Tk()
    root.withdraw()
    name = askopenfilename(initialdir=desktop_location,filetypes =(("Trade Files", "*.csv *.xls *.xlsx"),("All Files","*.*")),title = "Choose a file")
    return name

def set_bloxtaxfile(path):
    #reading from file and translating columns names to the project language
    file = pd.read_excel(path, error_bad_lines=False ,parse_dates = False ,object  = 'תאריך קניה')
    file = file.rename(columns={'כמות ביצוע':'Volume','תאריך מכירה':'Date_Sold','תאריך קניה':'Date_Acquired','נכס בסיס':'Symbol','תמורה':'Proceeds','עלות קניה שקלים':'Cost_Basis','רווח-הפסד שקלים (נומינלי)':'Gain'})
    file = file[['Symbol','Volume','Date_Acquired','Date_Sold','Proceeds','Cost_Basis','Gain']]

    #handling missings values in date acquired
    try:
        file.loc[file.Date_Acquired == '-' ,'Date_Acquired' ] = file.Date_Sold.astype(str)
        file.loc[file.Date_Acquired != '-','Date_Acquired'] = file.Date_Acquired.astype(str)
    except:
        pass
    file = file.rename(columns={'Date_Acquired': 'Date Acquired', 'Date_Sold': 'Date Sold', 'Cost_Basis': 'Cost Basis'})

    file['Proceeds'] = file['Gain'] + file['Cost Basis']
    file['Currency'] = 'ILS'
    file['Unmatched'] = ''

    #parse dates from string to date objects:
    file['Date Acquired'] = pd.to_datetime(file['Date Acquired']).dt.date
    file['Date Sold'] = pd.to_datetime(file['Date Sold']).dt.date


    return file
