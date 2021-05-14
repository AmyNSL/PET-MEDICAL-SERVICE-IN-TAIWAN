# -*- coding: utf-8 -*-
"""
PET MEDICAL SERVICE
"""
import requests as rq
import pandas as pd
import numpy as np
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from folium import plugins
import folium
import time
import selenium

jsonurl='https://data.coa.gov.tw/Service/OpenData/DataFileService.aspx?UnitId=078'
petRegisurl='https://www.pet.gov.tw/PetsMap/PetsMap.aspx'
#畫台灣行政區分界資料需用爬蟲
taiwancity='https://byronhu.wordpress.com/2013/09/09/%E5%8F%B0%E7%81%A3%E7%B8%A3%E5%B8%82%E7%B6%93%E7%B7%AF%E5%BA%A6/'


def rqResponse(url,linktype='wb'):
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'}
    ResponObj=rq.get(url,headers=headers)
    ResponObj.encoding =ResponObj.apparent_encoding
    if (ResponObj.status_code == 200) &(linktype=='wb'):
        return ResponObj.text
    elif (ResponObj.status_code == 200) &(linktype=='json'):
        return ResponObj.json()
    else:
        return "error: "+str(ResponObj.status_code)

def GoogleReviewScore(search_key,tagname,classname):
    url='https://www.google.com/search?q='+search_key+'&authuser=1&sxsrf=ALeKk03cgwLYEBNl8oVOkOP7VGVt1j5QKw%3A1619967550156&ei=Pr6OYMGNCa-xmAWmsaHYAg&oq='+search_key+'&gs_lcp=Cgdnd3Mtd2l6EAMyAggAMgIIJjoHCCMQsAMQJzoHCAAQRxCwAzoGCAAQBxAeOggIABAIEAcQHjoECCMQJzoECAAQQzoFCAAQzQJQ7rYBWMrVAWDC2AFoAXACeACAAUWIAZcEkgEBOZgBAKABAaoBB2d3cy13aXrIAQnAAQE&sclient=gws-wiz&ved=0ahUKEwjBpP-yoavwAhWvGKYKHaZYCCsQ4dUDCA4&uact=5'
    rs= rqResponse(url,linktype='wb')
    bsObj= BeautifulSoup(rs,'lxml')
    listbsObj=bsObj.find_all(tagname,{"class":classname})
    if len(listbsObj) >=1:
        return listbsObj[0].text
    else:
        return "No Result"
#review test    
#url='https://www.google.com/search?q=%E8%8F%AF%E7%94%9F%E5%8B%95%E7%89%A9%E9%86%AB%E9%99%A2&authuser=1&biw=1600&bih=722&sxsrf=ALeKk01gJz-S8bmWVDYmo66Sb5rHcBJJNA%3A1620748300086&ei=DKiaYMDbBI6JmAXZnrPACw&oq=%E8%8F%AF%E7%94%9F%E5%8B%95%E7%89%A9%E9%86%AB%E9%99%A2&gs_lcp=Cgdnd3Mtd2l6EAMyAggAMgYIABAFEB46BwgjEOoCECc6BAgAEB46BAgjECc6CAgAELEDEIMBOgUIABCxAzoECAAQDToFCAAQzQJQ6c3NCliH980KYKH8zQpoAXACeACAATiIAYAHkgECMTmYAQCgAQGqAQdnd3Mtd2l6sAEKwAEB&sclient=gws-wiz&ved=0ahUKEwjAkcn1_cHwAhWOBKYKHVnPDLgQ4dUDCA4&uact=5'
#print(GoogleReviewScore('奕良動物醫院','span','Aq14fc'))

#clean data
#incol is a list and each element is a dic:{col_name:[index,"default value"]}
#dropna= fill in True/only subset null[columns] or False
#dropdupli= [subset,inplace],dropdupli[0] is the subset to distiguish if it has duplicates,dropdupli[1] is inplace is True or False
#fillna= fill in number or False
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
    
jsonraw=rqResponse(jsonurl,linktype='json')
#print(jsonraw)
rawSelect=[]
for item in jsonraw:
    if item['狀態']=="開業":
        rawSelect.append([item['發照日期'],item['縣市'],item['機構名稱'],item['機構地址']])
pd_VMI= pd.DataFrame(rawSelect,columns=['發照日期','機構縣市','機構名稱','機構完整地址'])
pd_VMI= dataclean(pd_VMI,incol=[{'發照年YYYY':[1,'Unknown']},{'機構行政區':[3,'Unknown']},{'機構地址':[5,'Unknown']},{'Google評論分數':[7,'Unknown']}],fillna='NaN')
for i in range(0,len(pd_VMI['發照日期'])):
    if pd_VMI.iloc[i,0]!='':
        pd_VMI.iloc[i,1]=pd_VMI.iloc[i,0][0:4]
        pd_VMI.iloc[i,1]=datetime.strptime(pd_VMI.iloc[i,1], '%Y').strftime("%Y")
for i in range(0,len(pd_VMI['機構完整地址'])):
    pd_VMI.iloc[i,5]=pd_VMI.iloc[i,6][3:]

#Goolge Review
#for i in range(0,1910):
#    print(pd_VMI.iloc[i,4])
#   pd_VMI.iloc[i,7]=GoogleReviewScore(pd_VMI.iloc[i,4],'span','Aq14fc')
#   if i%200==0:
#       pd_VMI.to_csv('pd_VMI.csv',index=False)
#   time.sleep(0.08)
#pd_VMI.to_csv('pd_VMI.csv',index=False)

pd_VMI=pd.read_csv('pd_VMI.csv',encoding='utf-8')

#寵物登記raw data
url='https://www.pet.gov.tw/PetsMap/Handler_ENRF/MapApiCity.ashx?Area=0&iAddWith=JTdCJTIyQU5JTUFMJTIyOiUyMjIlMjIsJTIyU1BBWSUyMjolMjIyJTIyLCUyMlNJUkUlMjI6JTIyMCUyMiwlMjJQRVRTRVglMjI6JTIyMiUyMiwlMjJDb2xvciUyMjolMjJHJTIyLCUyMlNUJTIyOiUyMjIwMTEvMDEvMDElMjIsJTIyRUQlMjI6JTIyMjAyMS8wNS8wMyUyMiwlMjJBZGRyJTIyOiUyMiUyMiwlMjJpbnBUeXBlJTIyOiUyMkFkZHIlMjIlN0Q='
petrig=rqResponse(url,linktype='json')
countyReg=[]
for i in range(len(petrig)):
    countyReg.append([petrig[i]['CountyName'],petrig[i]['HouseCnt'],petrig[i]['cnt']])

CountyReg=pd.DataFrame(countyReg,columns=['登記縣市','登記戶數','登記隻數'])
print(CountyReg)
CountyReg= CountyReg.sort_values(by=['登記隻數'],ascending=False)
CountyReg= dataclean(CountyReg,incol=[{'每戶平均登記數':[3,'Unknown']}])
#register
sumHouse= CountyReg['登記戶數'].values.sum()
sumPet= CountyReg['登記隻數'].values.sum()
count=0
for i in CountyReg.loc[:,'每戶平均登記數']:
    i= CountyReg.iloc[count,2]/CountyReg.iloc[count,1]
    CountyReg.iloc[count,3]=i
    count+=1


count=0
for i in pd_VMI.loc[:,'Google評論分數']:
    if i=="No Result":
        i=''
        pd_VMI.iloc[count,7]=i
    count+=1

clincs_num=len(pd_VMI['機構名稱'].values)  

#by cities
pd_vetclinccity= pd_VMI.groupby('機構縣市')['機構名稱'].count()
pd_vetclinccity=pd_vetclinccity.sort_values(ascending=False)
    
#by year
pd_yearcreated= pd_VMI.groupby('發照年YYYY')['機構名稱'].count()
pd_yearcreated=pd_yearcreated.drop('Unknown',axis=0)
#print(pd_yearcreated.index)

#畫圖: show 台灣目前合法獸醫醫療診所總數,每個縣市平均的寵物醫療診所數量,寵物醫療院所成立的時間軸
fig=plt.figure(figsize=(10,13),dpi=120,edgecolor='#37474F')
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
#圖一左上
ax1= plt.subplot2grid((8,4),(0,0),colspan=2)
ax1.set_xticks([]) # 不要顯示x軸刻度
ax1.set_yticks([]) # 不要顯示y軸刻度
ax1.set_title('全台已登記寵物數量',fontsize=14)
ax1.text(0.5,0.4,'%d'%(sumPet),fontsize=36,fontweight='heavy',c='#37474F',ha='center')
#ax1.set_facecolor('#37474F')
#圖二右上
ax2= plt.subplot2grid((8,4),(0,2),colspan=2)
ax2.set_xticks([]) # 不要顯示x軸刻度
ax2.set_yticks([]) # 不要顯示y軸刻度
ax2.set_title('平均各縣市登記隻數',fontsize=14)
ax2.text(0.5,0.4,'%.1f'%(sumPet/len(CountyReg.index)),fontsize=36,fontweight='heavy',c='#37474F',ha='center')
ax2.text(0.85,0.3,'隻',fontsize=20,fontweight='heavy',c='#37474F',ha='center')
#ax2.set_facecolor('#37474F')
#圖三左二
ax3= plt.subplot2grid((8,4),(1,0),colspan=2)
ax3.set_xticks([]) # 不要顯示x軸刻度
ax3.set_yticks([]) # 不要顯示y軸刻度
ax3.set_title('全台總登記戶數',fontsize=14)
ax3.text(0.5,0.4,'%d'%(sumHouse),fontsize=36,fontweight='heavy',c='#37474F',ha='center')
#圖四右二
ax4= plt.subplot2grid((8,4),(1,2),colspan=2)
ax4.set_xticks([]) # 不要顯示x軸刻度
ax4.set_yticks([]) # 不要顯示y軸刻度
ax4.set_title('平均各縣市登記戶數',fontsize=14)
ax4.text(0.5,0.4,'%.1f'%(sumHouse/len(CountyReg.index)),fontsize=36,fontweight='heavy',c='#37474F',ha='center')
ax4.text(0.85,0.3,'戶',fontsize=20,fontweight='heavy',c='#37474F',ha='center')
#圖五中
ax5= plt.subplot2grid((8,4),(2,1),colspan=2)
ax5.set_xticks([]) # 不要顯示x軸刻度
ax5.set_yticks([]) # 不要顯示y軸刻度
ax5.set_title('每戶平均登記隻數',fontsize=14)
ax5.text(0.5,0.4,'%.1f'%(sumPet/sumHouse),fontsize=36,fontweight='heavy',c='#37474F',ha='center')
ax5.text(0.8,0.3,'隻',fontsize=20,fontweight='heavy',c='#37474F',ha='center')
#圖六中下
ax6= plt.subplot2grid((8,4),(3,0),rowspan=2,colspan=4)
ax7 = ax6.twinx()
ax6.plot(CountyReg['登記縣市'].values,CountyReg['登記隻數'].values,lw=1.2,color="#616161")
ax6.set_ylim([0,max(CountyReg['登記隻數'].values)+50000])
ax6.set_xticklabels(CountyReg['登記縣市'].values,rotation=90,fontsize=11.5)
#ax6.axhline(sumPet/len(CountyReg.index), color='#37474F', lw=1.5, alpha=0.8,ls='--')
#ax6.text(CountyReg.index[-6],(sumPet/len(CountyReg.index))+500,"平均各縣市寵物登記數: %.1f"%(sumPet/len(CountyReg.index)),c='black',fontsize=11.5,fontweight="bold")
ax6.set_ylabel('登記總數量(隻)', color='#616161',fontsize=11.5)
ax6.tick_params(axis='y',labelcolor='#616161')
ax6.set_title('縣市分布概況',fontsize=14)
ax7.plot(CountyReg['登記縣市'].values,CountyReg['每戶平均登記數'].values,lw=1.2,color='#186a93ff') 
ax7.set_ylabel('平均登記數(隻/戶)', color='#186a93ff',fontsize=11.5)
ax7.set_ylim([0,max(CountyReg['每戶平均登記數'].values)+1])
ax7.tick_params(axis='y',labelcolor='#186a93ff')
#圖八底部
ax8= plt.subplot2grid((8,4),(5,0),rowspan=3,colspan=4)
ax8.scatter(CountyReg['登記隻數'].values,CountyReg['每戶平均登記數'].values,marker='^',c='#027dbbff')
ax8.set_xlabel("登記總數量(隻)",fontsize=11)
ax8.set_ylabel('平均登記數(隻/戶)',fontsize=11)
ax8.axvline(sumPet/len(CountyReg.index),c="#eea904ff",lw=1.2)
ax8.axhline(y=sumPet/sumHouse,c="#eea904ff",lw=1.2)
ax8.text(sumPet/len(CountyReg.index),sumPet/sumHouse,"Avg.\n(%.2f,%.2f)"%(sumPet/len(CountyReg.index),sumPet/sumHouse), ha="center", va="center",size=10.5,
    bbox=dict(boxstyle="circle,pad=0.3", fc="#fbc11cff", ec="#eea904ff", lw=0.5))
ax8.set_title("各縣市 登記總數 v.s 每戶平均登記數",fontsize=14)
for i in range(len(CountyReg.index)):
    if CountyReg.iloc[i,2]>= (sumPet/len(CountyReg.index)):
        ax8.text(CountyReg.iloc[i,2],CountyReg.iloc[i,3]+0.03,CountyReg.iloc[i,0],fontsize=10.5,c='#027dbbff',fontweight='bold')

for ax, color in zip([ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8], ['white', 'white', 'white', 'white', 'white','white', 'white', 'white']):
    plt.setp(ax.spines.values(), color=color)
    plt.setp([ax.get_xticklines(), ax.get_yticklines()], color=color)

fig.suptitle('台灣寵物飼養登記概況',fontsize=20,fontweight='bold',y=1.05)
plt.tight_layout()
plt.savefig('台灣寵物飼養登記概況.png',pad_inches=0.0)#pad_inches: 去除所有白邊
plt.show()




#畫圖: show 台灣目前合法獸醫醫療診所總數,每個縣市平均的寵物醫療診所數量,寵物醫療院所成立的時間軸
fig=plt.figure(figsize=(8.5,12),dpi=120,edgecolor='#37474F')
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
#圖一左上
ax1= plt.subplot2grid((6,4),(0,0),colspan=2)
ax1.set_xticks([]) # 不要顯示x軸刻度
ax1.set_yticks([]) # 不要顯示y軸刻度
ax1.set_title('合法獸醫醫療診所總數',fontsize=14)
ax1.text(0.5,0.4,'%d'%(clincs_num),fontsize=36,fontweight='heavy',c='#37474F',ha='center')
#ax1.set_facecolor('#37474F')
#圖二右上
ax2= plt.subplot2grid((6,4),(0,2),colspan=2)
ax2.set_xticks([]) # 不要顯示x軸刻度
ax2.set_yticks([]) # 不要顯示y軸刻度
ax2.set_title('平均各縣市獸醫院所數量',fontsize=14)
ax2.text(0.5,0.4,'%.1f'%(clincs_num/len(pd_vetclinccity.index)),fontsize=36,fontweight='heavy',c='#37474F',ha='center')
ax2.text(0.8,0.3,'間',fontsize=20,fontweight='heavy',c='#37474F',ha='center')
#ax2.set_facecolor('#37474F')
#圖三中間
ax3= plt.subplot2grid((6,4),(1,0),rowspan=2,colspan=4)
ax3.plot(pd_yearcreated.index,pd_yearcreated.values,lw=1.3,color='#37474F',label='合法發照設立獸醫診所')
ax3.set_ylim([0,max(pd_yearcreated.values)+50])
ax3.set_xticklabels(pd_yearcreated.index,rotation=90,fontsize=10.5)
ax3.legend(loc='best',fontsize=12)
ax3.set_xlabel('西元年YYYY',fontsize=10)
ax3.set_title('歷年獸醫醫療院所設立趨勢',fontsize=14)
#圖四底部
ax4= plt.subplot2grid((6,4),(3,0),rowspan=3,colspan=4)
ax4.bar(pd_vetclinccity.index,pd_vetclinccity.values,width=0.9,color="#78909c")
ax4.set_ylim([0,max(pd_vetclinccity.values)+50])
ax4.set_xticklabels(pd_vetclinccity.index,rotation=90,fontsize=11.5)
for i in range(len(pd_vetclinccity.index)):
    ax4.text(pd_vetclinccity.index[i],pd_vetclinccity.values[i]+10,pd_vetclinccity.values[i],c='black',fontsize=11.5)
ax4.axhline(clincs_num/len(pd_vetclinccity.index), color='#37474F', lw=1.5, alpha=0.8,ls='--')
ax4.text(pd_vetclinccity.index[-6],(clincs_num/len(pd_vetclinccity.index))+10,"平均各縣市獸醫院所數量: %.1f"%(clincs_num/len(pd_vetclinccity.index)),c='black',fontsize=11.5,fontweight="bold")
ax4.set_title('縣市分布概況',fontsize=14)
for ax, color in zip([ax1, ax2, ax3, ax4], ['white', 'white', 'white', 'white']):
    plt.setp(ax.spines.values(), color=color)
    plt.setp([ax.get_xticklines(), ax.get_yticklines()], color=color)
fig.suptitle('台灣獸醫院所資源概況說明',fontsize=20,fontweight='bold',y=1.05)
plt.tight_layout()
plt.savefig('台灣獸醫院所資源概況說明.png',pad_inches=0.0)#pad_inches: 去除所有白邊
plt.show()

#畫台灣地圖前置作業
Latilongi=[]
bsObj=BeautifulSoup(rqResponse(taiwancity,linktype='wb'),'lxml')
data= bsObj.find_all('tr')
for i in range(len(data)):
    new=data[i].text.split('\n')
    Latilongi.append([new[2],new[5],new[8]])
    #print(new)    
pd_Latilongi=pd.DataFrame(Latilongi,columns=['機構縣市','經度','緯度'])
pd_Latilongi.iloc[4,0]='桃園市'
pd_vetclinccity=pd.merge(pd_vetclinccity,pd_Latilongi,on='機構縣市',how='outer')
count=0
for i in pd_vetclinccity.loc[:,'機構名稱']:
    #print(i,type(i))
    i=str(i)
    if i=="nan":
        pd_vetclinccity.iloc[count,1]=0.0
    else:
        pd_vetclinccity.iloc[count,1]=float(i)
    count+=1
    
# define the national map
national_map = folium.Map(location=[23.9037,120.5955],tiles='cartodbpositron',zoom_start=7.5,width='100%',height='100%')

for lat, lng, label, city, in zip(pd_vetclinccity['緯度'].values, pd_vetclinccity['經度'].values, pd_vetclinccity['機構名稱'].values,pd_vetclinccity['機構縣市'].values):
    html = '<h3>'+city+'</h3><br>合法獸醫院所:'+str(label)+'間'
    iframe = folium.IFrame(html)
    popup = folium.Popup(iframe,
                     min_width=220,max_width=220)
    if label!=0.0:
        radius=label/6
        folium.CircleMarker(location=[lat, lng],radius=radius,
                            fill=True,fill_opacity=0.7,
                            color='yellow',opacity=0.9,
                            fill_color='red',
                            popup=popup,
                            #popup="%s\n合法獸醫院所: %d 間"%(city,label),
                            ).add_to(national_map)
    else:
        radius=0.2
        folium.CircleMarker(location=[lat, lng],radius=radius,
                            fill=True,fill_opacity=0.7,
                            color='yellow',opacity=0.9,
                            fill_color='red',
                            popup=popup,
                            #popup="%s\n合法獸醫院所: %d 間"%(city,label),
                            ).add_to(national_map)
# instantiate a mark cluster object for the incidents in the dataframe
#incidents = plugins.MarkerCluster().add_to(national_map)
# loop through the dataframe and add each data point to the mark cluster
#for lat, lng, label, in zip(pd_vetclinccity['緯度'].values, pd_vetclinccity['經度'].values, pd_vetclinccity['機構名稱'].values):
#    print(lat, lng, label)
#    folium.Marker(
#        location=[lat, lng],
#        icon=None,
#        popup=label,
#    ).add_to(incidents)

# add incidents to map
#national_map.add_child(incidents)

national_map.save('taiwan.html')