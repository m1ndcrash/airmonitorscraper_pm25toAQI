# -*- coding: utf-8 -*-
"""
Created on Sat Sep 26 09:05:30 2020

@author: mindcrash
"""
import pandas as pd
from datetime import datetime

air_zones = ('Southern_Interior', 'Central_Interior', 'Coastal', 'Georgia_Strait', 'Lower_Fraser_Valley', 'Northeast')
pollutants = ['O3', 'CO', 'NO2', 'SO2', 'PM25']
columns = pollutants + ['SID',]
units = ['ppb','ppm','ppb','ppb','ug/m3']
years = (2016, 2017, 2018, 2019, 2020)

aqi_classes = ((0,50), (51,100), (101,150), (151,200), (201,300), (301,400), (401,500))
pm25_classes = ((0.0,12.0), (12.0, 35.4), (35.4,55.4), (55.4,150.4), (150.4,250.4), (250.4,350.4), (350.4,500.4))

def classBreak(val, classes):
    for i, c in enumerate(classes):
        if val > c[0] and val < c[1]:
            return i
    return False

# parse the weird date format
def dateParser(date_str):
    date_str = date_str.replace(" 24", " 12")
    date_list = date_str.split(' ')
    if len(date_list[1]) == 4:
        date_list[1] = '0' + date_list[1]
    return datetime.strptime(' '.join(date_list), '%m/%d/%Y %I:%M %p')

#import & process csv	
    df = pd.read_csv('data/{}.csv'.format(air_zone), header=0, 
                     index_col=['Date Time'], parse_dates=True, date_parser=dateParser, na_values=['--'])

    df = df[[c for c in df.columns if c in columns]]
    df = df.apply(pd.to_numeric, errors='coerce')
    df.sort_index(inplace=True, ascending=True)


# extract 
    for year in years:

        aqi = []
        
        dates = pd.date_range(start='03/18/'+str(year), end='05/16/'+str(year))

        for i in range(len(dates)):

            day_data = df.loc[dates[i-1]:dates[i]]
            day_data.between_time('15:00','19:00')
            pm25 = [val for val in day_data['PM25'].tolist() if str(val) !='nan']

            if len(pm25) < 10:
                continue

            pm25_min, pm25_max, pm25_mean = min(pm25), max(pm25), sum(pm25)/len(pm25)

            pm25_break = classBreak(pm25_mean, pm25_classes)

            pm25_aqi = round((aqi_classes[pm25_break][1]-aqi_classes[pm25_break][0])/(pm25_max-pm25_min) * (round(pm25_mean, 2)-pm25_min) + aqi_classes[pm25_break][0])

            aqi.append(pm25_aqi)

        aqi_min, aqi_max, aqi_mean = min(aqi), max(aqi), sum(aqi)/len(aqi)
        d = {'YEAR':year, 'MIN': aqi_min, 'MAX': aqi_max, 'MEAN': aqi_mean, 'ZONE':air_zone+'_'+str(years.index(year))}
        out.loc[index] = d
        index += 1