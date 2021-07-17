# -*- coding: utf-8 -*-
"""
Webcrawlwer.exe
"""
import time
from datetime import datetime
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import pandas as pd
import sqlite3

def dataclean(data,delcol=None,delindex=None,incol=None,dropna=False,dropdupli=False,fillna=False):
    if delcol != None:
        for name in delcol:
            data=data.drop(name,axis=1)
    if delindex != None:
        for i in delindex:
            data=data.drop(i,axis=0)
    if incol != None:
        for k in incol:    
            for i,j in k.items():
                data.insert(j[0],i,j[1])
    if dropna != False:
        data=data.dropna(subset=dropna)
    if fillna != False:
        data=data.fillna(fillna)
    if dropdupli != False:
        data.drop_duplicates(subset=dropdupli[0], keep='first', inplace=dropdupli[1], ignore_index=False)
    return data

today=datetime.now().strftime('%Y-%m-%d')
url = 'https://www.pet.gov.tw/Web/O302.aspx'
"=================抓取前置作業===================="

print('寵物登記原始資料自動抓取執行檔')

data_period=input('請問需要年度資料或是任意時間段: \n年度資料請輸入A,任意時間段請輸入B :')
data_period = data_period.capitalize()
dataPeriod=[]
if data_period=='A':
    year = input('請輸入年分(yyyy),多年資料請以「,」區隔:')
    year_list = year.split(',')
    for i in range(len(year_list)):
        dataPeriod.append([year_list[i]+'/01/01',year_list[i]+'/12/31'])        
elif data_period=='B':
    start_date = input('請輸入起始日(yyyy/mm/dd):')
    end_date = input('請輸入結束日(yyyy/mm/dd):')
    dataPeriod.append([start_date,end_date])

timstamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
print('目前時間: %s 準備開始執行'%timstamp)

"=================開始擷取===================="

driver= webdriver.Chrome("chromedriver")
driver.implicitly_wait(5) #靜默等待__秒,為的是確保所有網頁資料都全部載入可以擷取完整網頁
driver.get(url)
print(driver.title)
time.sleep(3)

for i in range(len(dataPeriod)):
    #輸入查詢的作業時間年月日 (yyyy/mm/dd)
    driver.find_element_by_id('txtSDATE').send_keys(dataPeriod[i][0])
    time.sleep(2)
    driver.find_element_by_id('txtEDATE').send_keys(dataPeriod[i][1])
    time.sleep(2)
    print('請稍後,資料讀取中......')
    circle_buttonXpath=['//*[@id="aspnetForm"]/div[4]/div/section/div[2]/div/div/div[2]/div[3]/div/div/label/span',
                    '//*[@id="aspnetForm"]/div[4]/div/section/div[2]/div/div/div[2]/div[4]/div/div/label/span']
    #狗狗 [0],貓貓[1]

    '''建立db準備'''
    #連線指定資料庫
    conObj = sqlite3.connect('pet.db')
    timstamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    print('%s: [Info]Successfully connect to db'%timstamp)
    #建立cursor物件
    cursor = conObj.cursor()
    
    '''資料解析開始'''
    count=0
    while count<2:
        driver.find_element_by_xpath(circle_buttonXpath[count]).click()
        driver.find_element_by_id('aSearch').click()
        time.sleep(3)
        html= driver.page_source
        bsObj= bs(html,'lxml')
        petType= bsObj.find_all(class_='form-check-input')
        table= bsObj.select_one('#CountTown')#貼上 css selector路徑
        df= pd.read_html(str(table)) #有可能抓到不只一個表格,會以串列方式儲存
        df[0]=dataclean(df[0],delindex=[22],incol=[{'petType':[1,petType[count+1].get('id')]}]) #利用id作為作為分類名稱
        if data_period=='A':
            df[0]=dataclean(df[0],incol=[{'Year':[2,year_list[i]]}])
        #將columns name存成list
        columns=df[0].columns.values.tolist()
        #建立資料表,輸入SQL語法,此語法被視為字串在py內
        if data_period=='A':
            sqlString = '''CREATE TABLE IF NOT EXISTS petRaw(
            "{0}" TEXT,
            "{1}" TEXT,
            "{2}" TEXT,
            "{3}" INTEGER,
            "{4}" INTEGER,
            "{5}" INTEGER,
            "{6}" INTEGER,
            "{7}" INTEGER,
            "{8}" INTEGER,
            "{9}" INTEGER,
            "{10}" INTEGER,
            "{11}" FLOAT,
            "{12}" FLOAT
            )'''
            sqlString = sqlString.format(columns[0],columns[1],columns[2],columns[3],
                                         columns[4],columns[5],columns[6],columns[7],
                                         columns[8],columns[9],columns[10],columns[11],columns[12])
            cursor.execute(sqlString)
            timstamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print('%s: [Info]Successfully create table and columns'%timstamp)
            #Insert data into db table
            for j in range(len(df[0].index)):
                cell = '''INSERT INTO petRaw
                VALUES ("{0}","{1}","{2}",{3},{4},{5},{6},{7},{8},{9},{10},{11},{12})'''
                cell = cell.format(df[0].iloc[j,0],df[0].iloc[j,1],df[0].iloc[j,2],df[0].iloc[j,3],
                                   df[0].iloc[j,4],df[0].iloc[j,5],df[0].iloc[j,6],df[0].iloc[j,7],
                                   df[0].iloc[j,8],df[0].iloc[j,9],df[0].iloc[j,10],df[0].iloc[j,11],df[0].iloc[j,12])
                cursor.execute(cell)
        elif data_period=='B':
            sqlString = '''CREATE TABLE IF NOT EXISTS petRaw1(
            "{0}" TEXT,
            "{1}" TEXT,
            "{2}" INTEGER,
            "{3}" INTEGER,
            "{4}" INTEGER,
            "{5}" INTEGER,
            "{6}" INTEGER,
            "{7}" INTEGER,
            "{8}" INTEGER,
            "{9}" INTEGER,
            "{10}" FLOAT,
            "{11}" FLOAT
            )'''
            sqlString = sqlString.format(columns[0],columns[1],columns[2],columns[3],
                                         columns[4],columns[5],columns[6],columns[7],
                                         columns[8],columns[9],columns[10],columns[11])
            cursor.execute(sqlString)
            timstamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print('%s: [Info]Successfully create table and columns'%timstamp)
            #Insert data into db table
            for j in range(len(df[0].index)):
                cell = '''INSERT INTO petRaw1
                VALUES ("{0}","{1}",{2},{3},{4},{5},{6},{7},{8},{9},{10},{11})'''
                cell = cell.format(df[0].iloc[j,0],df[0].iloc[j,1],df[0].iloc[j,2],df[0].iloc[j,3],
                                   df[0].iloc[j,4],df[0].iloc[j,5],df[0].iloc[j,6],df[0].iloc[j,7],
                                   df[0].iloc[j,8],df[0].iloc[j,9],df[0].iloc[j,10],df[0].iloc[j,11])
                cursor.execute(cell) 
        if count==0:
            filename1= 'petsterilization_'+petType[count+1].get('id')+today+'.csv'
            df[0].to_csv(filename1,index=False,encoding='utf-8')
        elif count==1:
            filename2= 'petsterilization_'+petType[count+1].get('id')+today+'.csv'
            df[0].to_csv(filename2,index=False,encoding='utf-8')
        today_timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print("%s: [Info]資料寫入檔案 %s成功"%(today_timestamp,'petsterilization_'+petType[count+1].get('id')+today+'.csv'))
        count+=1
        time.sleep(6)            
    #主動更新所有execute
    conObj.commit()
    timstamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print('%s: [Info]Commit updated'%timstamp)
timstamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print('%s: [Info]Complete all steps, ready to close db'%timstamp)
#關閉資料庫
conObj.close()
print('全部資料寫入成功')
time.sleep(3)
driver.quit()