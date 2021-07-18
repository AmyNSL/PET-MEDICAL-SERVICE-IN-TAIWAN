# -*- coding: utf-8 -*-
"""
Project2
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
driver= webdriver.Chrome("chromedriver")
driver.implicitly_wait(5) #靜默等待__秒,為的是確保所有網頁資料都全部載入可以擷取完整網頁
driver.get(url)
print(driver.title)

time.sleep(3)
#輸入查詢的作業時間年月日 (yyyy/mm/dd)

driver.find_element_by_id('txtSDATE').send_keys('2011/01/01')
time.sleep(2)
driver.find_element_by_id('txtEDATE').send_keys('2021/06/30')
time.sleep(2)
print('請稍後,資料讀取中......')

circle_buttonXpath=['//*[@id="aspnetForm"]/div[4]/div/section/div[2]/div/div/div[2]/div[3]/div/div/label/span',
                    '//*[@id="aspnetForm"]/div[4]/div/section/div[2]/div/div/div[2]/div[4]/div/div/label/span']
#狗狗 [0],貓貓[1]

'''建立db準備'''
#連線指定資料庫
conObj = sqlite3.connect('Project2021_pet.db')
timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
print('%s: [Info]Successfully connect to db'%timestamp)
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
    #將columns name存成list
    columns=df[0].columns.values.tolist()
    #建立資料表,輸入SQL語法,此語法被視為字串在py內
    sqlString = '''CREATE TABLE IF NOT EXISTS petSterilization(
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
    #print(sqlString)
    cursor.execute(sqlString)
    timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print('%s: [Info]Successfully create table and columns'%timestamp)
    for i in range(len(df[0].index)):
        #Insert data into db table
        cell = '''INSERT INTO petSterilization
        VALUES ("{0}","{1}",{2},{3},{4},{5},{6},{7},{8},{9},{10},{11})'''
        cell = cell.format(df[0].iloc[i,0],df[0].iloc[i,1],df[0].iloc[i,2],df[0].iloc[i,3],
                           df[0].iloc[i,4],df[0].iloc[i,5],df[0].iloc[i,6],df[0].iloc[i,7],
                           df[0].iloc[i,8],df[0].iloc[i,9],df[0].iloc[i,10],df[0].iloc[i,11])
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
timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print('%s: [Info]Complete all steps, ready to close db'%timestamp)

#關閉資料庫
conObj.close()
print('全部資料寫入成功')
driver.quit()

"""======================資料收集完成,開始分析======================="""

import matplotlib.pyplot as plt

def importF(filename,encoding='utf-8',sep=","):   
    raw=pd.read_csv(filename,encoding=encoding,sep=sep)
    return raw

raw1= importF(filename1,encoding='utf-8',sep=",")
raw2= importF(filename2,encoding='utf-8',sep=",")

frames = [raw1, raw2]
petSterdata=pd.concat(frames)
#print(petSterdata.columns.values.tolist())
petSterdata.rename(columns = {'絕育率  (E-F)/(A-B)':'絕育率'}, inplace =True)
avgSter = petSterdata.groupby('縣市')['絕育率'].mean()
dogSterdata = petSterdata.query('petType=="Dog"')[['縣市','絕育率']]
dogSterdata.rename(columns = {'絕育率':'絕育率(狗)'}, inplace =True)
catSterdata = petSterdata.query('petType=="Cat"')[['縣市','絕育率']]
catSterdata.rename(columns = {'絕育率':'絕育率(貓)'}, inplace =True)

countySterrate = pd.merge(avgSter,dogSterdata,left_index=True,right_on = '縣市',how='inner')
countySterrate = pd.merge(countySterrate,catSterdata,on='縣市',how='inner')
#adjust the order
countySterrate = countySterrate[['縣市','絕育率','絕育率(狗)','絕育率(貓)']]
countySterrate = countySterrate.sort_values('絕育率',ascending=False)


#絕育率 = (E-F)/(A-B)
overallSterRate = countySterrate['絕育率'].mean()
dogSterRate = countySterrate['絕育率(狗)'].mean()
catSterRate = countySterrate['絕育率(貓)'].mean()
'''PLOT'''
fig=plt.figure(figsize=(15,11),dpi=150,edgecolor='#37474F')
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
subplot=[]
#圖一左上
ax1= plt.subplot2grid((4,6),(0,0),colspan=2)
subplot.append(ax1)
ax1.set_xticks([]) # 不要顯示x軸刻度
ax1.set_yticks([]) # 不要顯示y軸刻度
ax1.set_title('全台寵物平均絕育率',fontsize=14)
ax1.text(0.5,0.55,'%.2f%%'%(overallSterRate),fontsize=38,fontweight='heavy',c='#37474F',ha='center')
#圖二左中
ax2= plt.subplot2grid((4,6),(1,0))
subplot.append(ax2)
ax2.set_xticks([]) # 不要顯示x軸刻度
ax2.set_yticks([]) # 不要顯示y軸刻度
ax2.set_title('平均絕育率(狗狗)',fontsize=14)
ax2.text(0.5,0.5,'%.2f%%'%(dogSterRate),fontsize=32,fontweight='heavy',c='#37474F',ha='center')
#圖三左中
ax3= plt.subplot2grid((4,6),(1,1))
subplot.append(ax3)
ax3.set_xticks([]) # 不要顯示x軸刻度
ax3.set_yticks([]) # 不要顯示y軸刻度
ax3.set_title('平均絕育率(貓貓)',fontsize=14)
ax3.text(0.5,0.5,'%.2f%%'%(catSterRate),fontsize=32,fontweight='heavy',c='#37474F',ha='center')
#圖四左下
ax4= plt.subplot2grid((4,6),(2,0),colspan=2,rowspan=2)
subplot.append(ax4)
ax4.bar(countySterrate['縣市'].values,countySterrate['絕育率'].values,width=0.8,color="#78909c")
ax4.set_title('各縣市絕育率概況',fontsize=14)
ax4.set_ylabel('絕育率(%)',fontsize=11)
ax4.set_xlabel('縣市',fontsize=11)
ax4.set_xticklabels(countySterrate['縣市'].values,rotation=90,fontsize=12)
#圖五右
ax5= plt.subplot2grid((4,6),(0,2),colspan=4,rowspan=4)
subplot.append(ax5)
ax5.scatter(countySterrate['絕育率(狗)'].values,countySterrate['絕育率(貓)'].values,marker='^',c='#06aab6ff')
ax5.set_title('貓狗絕育率分布概況',fontsize=14)
ax5.set_xlabel('絕育率(%)_狗狗',fontsize=12)
ax5.set_ylabel('絕育率(%)_貓貓',fontsize=12)
ax5.axvline(dogSterRate,c="#eea904ff",lw=1.2)
ax5.axhline(y=catSterRate,c="#eea904ff",lw=1.2)

ax5.set_ylim([min(countySterrate['絕育率(貓)'].values)-2,max(countySterrate['絕育率(貓)'].values)+2])
ax5.set_xlim([min(countySterrate['絕育率(狗)'].values)-5,max(countySterrate['絕育率(狗)'].values)+5])
for i in range(len(countySterrate)):
    if (countySterrate.iloc[i,2]<dogSterRate) or (countySterrate.iloc[i,3]<catSterRate):
        ax5.text(countySterrate.iloc[i,2],countySterrate.iloc[i,3]-1,countySterrate.iloc[i,0],fontsize=12,c='#06aab6ff',rotation=60)

for ax, color in zip(subplot, ['white']*5):
    plt.setp(ax.spines.values(), color=color)
    plt.setp([ax.get_xticklines(), ax.get_yticklines()], color=color)

fig.suptitle('寵物絕育概況 (2011-迄今)',fontsize=22,fontweight='bold',y=1.02)
fig.tight_layout()
plt.savefig('台灣寵物絕育狀況.png',dpi=180, bbox_inches = "tight")#pad_inches: 去除所有白邊
plt.show()

