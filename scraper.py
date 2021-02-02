# -*- coding: utf-8 -*-
"""
Created on Mon Oct 26 11:07:41 2020

@author: mindcrash

intended display
https://www.esri.com/about/newsroom/arcuser/looking-at-temporal-changes/
"""

from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import Select

import re
import pandas as pd
import time
import sys

browser = Firefox()

start_date = '03/18/'
end_date = '05/18/'
years = (2016, 2017, 2018, 2019, 2020)

link = 'https://envistaweb.env.gov.bc.ca/StationReportFast.aspx?ST_ID='

# BC airzones
air_zones = ('Southern Interior', 'Central Interior', 'Coastal', 'Georgia Strait', 'Lower Fraiser Valley', 'Northeast')

air_zone = dict()
# southern bc
air_zone['Southern Interior'] = (419, 550, 11, 267, 571)
# central interiror
air_zone['Central Interior'] = (13, 575, 560, 16)
# coastal 
air_zone['Coastal'] = (78, 546, 471)
# georgia strait
air_zone['Georgia Strait'] = (284, 414, 542, 10, 130, 491, 4, 197)
# lower fraiser valley
air_zone['Lower Fraiser Valley'] = (256, 428, 261, 249, 257, 256, 246, 244, 247, 273, 259)
# nothern bc
air_zone['Northeast'] = (469, 578)

counter = 0

for zone in air_zone.keys():
    data = []
    for sid in air_zone[zone]:
        for year in years:
            
            browser.get(link + str(sid))

            radio1 = browser.find_element_by_id('RadioButtonList2_3')
            radio1.click()
    
            start_date_form = browser.find_element_by_id('BasicDatePicker1_TextBox')
            start_date_form.clear()
            start_date_form.send_keys(start_date + str(year))
    
            end_date_form = browser.find_element_by_id('BasicDatePicker2_TextBox')
            end_date_form.clear()
            end_date_form.send_keys(end_date + str(year))
    
            select = Select(browser.find_element_by_id('ddlTimeBase'))
            select.select_by_value('60')
    
            search_button = browser.find_element_by_id('btnGenerateReport')
            search_button.click()
            time.sleep(3)
    
            # regex the data
            m = re.search(r"strHTML='<html>(.*)</html>'", browser.page_source, re.DOTALL)
            match = m.group()
            # create data frame
            df = pd.read_html(match, header=0)[0]
            
            # clean dataframe
            df.drop(index=[0,1], inplace=True)
            df.drop(index=[i for i in range(1463,1474)], inplace=True)
            df['SID'] = sid
            df['ZONE'] = air_zones.index(zone)

            data.append(df)
            print(zone, sid, year, "complete")
            print(df.head())
            """
            if counter == 1: 
                result = pd.concat(data)
                path_to_data = r'data\\data.csv'
                result.to_csv(path_to_data, index = False)
                sys.exit()
            """    
            counter += 1
    
    result = pd.concat(data)
    path_to_data = r'data\\{}.csv'.format(zone)
    result.to_csv(path_to_data, index = False)

browser.close()
