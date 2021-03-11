import pandas as pd
import pickle
from datetime import datetime, timedelta
from pandas_datareader import data


stocks = ['ccl','ko','t','aapl','txn','msft','amzn','azo', 'nvr']
columns_data = ['growth_rate', 'growth_jobs', 'High', 'Low', 'Open', 'Adj Close', 'quarter', 'Year', 'month_y', 'day']

#Open models for each stock.
xgb_model = []
for i in stocks:
    xgb_model.append(pickle.load(open(f'./model_pickle/model_{i}.p','rb')))



#Get todays date
def today_date():
    date = datetime.today()
    if date.weekday() == 6:
        date = date.today() - 2*timedelta(days=1)
    elif date.weekday() == 0:
        date = date.today() - 3 * timedelta(days=1)
    else:
        date = datetime.today()- timedelta(days=1)
    date_list = [1]
    date_list.append(date.year)
    date_list.append(date.month)
    date_list.append(date.day)
    return date_list

#Get todays values
def last_values(ticker):
    date = datetime.today()
    if date.weekday() == 6:
        date = date.today().date() - timedelta(days=2)
    elif date.weekday() ==0:
        date = date.today().date() - timedelta(days=3)
    else:
        date = datetime.today().date()- timedelta(days=1)
    key_values = []
    last_value = data.DataReader(ticker, start = date, end= date ,data_source='yahoo').values[0]
    key_values.append(last_value[0])
    key_values.append(last_value[1])
    key_values.append(last_value[2])
    key_values.append(last_value[-1])
    return key_values,last_value[3]

#Get todays dataframe
def stock_model(ticker):
    gdp_labor = [1.500426, 2.134474]
    stock_values = []
    stock_values.extend(gdp_labor)
    stock_values.extend(last_values(ticker)[0])
    stock_values.extend(today_date())
    return stock_values

#Gets prices for tomorrow
yesterday_list = []
variation_list = []
predicted_list = []
for i in range(len(stocks)):
    model_values = pd.DataFrame([stock_model(stocks[i])], columns = columns_data)
    yesterday_price= round(last_values(stocks[i])[1],2)
    predicted_price = round(xgb_model[i].predict(model_values)[0],2)
    variation_price = round((predicted_price-yesterday_price)/yesterday_price*100,2)

    predicted_list.append(predicted_price)
    yesterday_list.append(yesterday_price)
    variation_list.append(variation_price)
    #print(stocks[i] + ' - ' + str(predicted_price))
    #print('Yesterday price closed at '+ str(yesterday_price))
    #print(str(variation_price)+'%')

