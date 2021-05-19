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
import seaborn as sns
import math

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
pd_VMI.iloc[707,4]='左營家畜醫院'
#Goolge Review
#for i in range(0,1910):
#    print(pd_VMI.iloc[i,4])
#   pd_VMI.iloc[i,7]=GoogleReviewScore(pd_VMI.iloc[i,4],'span','Aq14fc')
#   if i%200==0:
#       pd_VMI.to_csv('pd_VMI.csv',index=False)
#   time.sleep(0.08)
#pd_VMI.to_csv('pd_VMI.csv',index=False)


pd_VMI=pd.read_csv('pd_VMI.csv',encoding='utf-8')
pd_VMI= dataclean(pd_VMI,incol=[{'評論分數區間':[8,'Null']},{'Count':[9,1]}])

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
    


#google review
count=0
for i in pd_VMI.loc[:,'Google評論分數']:
    if i=="No Result":
        i=np.nan
        pd_VMI.iloc[count,7]=i
    count+=1

avgarray=[]
for i in range(len(pd_VMI['Google評論分數'].index)):
    if pd_VMI.iloc[i,7]!=np.nan:
        pd_VMI.iloc[i,7]=float(pd_VMI.iloc[i,7])
        avgarray.append(pd_VMI.iloc[i,7])
        if pd_VMI.iloc[i,7]>=4:
            pd_VMI.iloc[i,8]='4-5'
        elif pd_VMI.iloc[i,7]>=3:
            pd_VMI.iloc[i,8]='3-4'
        elif pd_VMI.iloc[i,7]>=1:
            pd_VMI.iloc[i,8]='1-3'
    else:
        pd_VMI.iloc[i,8]='無評分'


gr=pd_VMI.groupby('評論分數區間')['機構名稱'].count()
clincs_num=len(pd_VMI['機構名稱'].values)  
count_rate=clincs_num-gr.iloc[3]
review_table=pd.pivot_table(pd_VMI,values='Count',index=['機構縣市'],columns=['評論分數區間'], aggfunc=np.sum,fill_value=0)
review_table= review_table.reindex(review_table.sort_values(by=['4-5'],ascending=False).index)

#by cities
pd_vetclinccity= pd_VMI.groupby('機構縣市')['機構名稱'].count()
pd_vetclinccity=pd_vetclinccity.sort_values(ascending=False)

pd_pet= pd.merge(pd_vetclinccity,CountyReg,left_on='機構縣市',right_on='登記縣市',how='outer')
pd_pet.rename(columns = {'機構名稱': '機構數量'}, inplace =True)
pd_pet = dataclean(pd_pet,incol=[{'平均各機構負載':[1,'']}])
pd_pet.iloc[21,0],pd_pet.iloc[21,1]=0,-pd_pet.iloc[21,4]

for i in range(len(pd_pet.index)):
    if pd_pet.iloc[i,0] !=0:
        pd_pet.iloc[i,1]=pd_pet.iloc[i,4]/pd_pet.iloc[i,0]


pd_grrate= pd_VMI.groupby('機構縣市')['Google評論分數','評論分數區間'].count()
pd_grrate= dataclean(pd_grrate,incol=[{'評分率':[2,'']}])

pd_gr= pd_VMI.groupby('機構縣市')['Google評論分數'].sum()
pd_gr= pd.merge(pd_gr,pd_grrate,on='機構縣市',how='outer')
pd_gr= dataclean(pd_gr,incol=[{'平均評分':[4,'']}])
for i in range(len(pd_gr.index)):
    pd_gr.iloc[i,4]=pd_gr.iloc[i,0]/pd_gr.iloc[i,1]
pd_gr=pd_gr.sort_values(by=['平均評分'],ascending=False)
avggr=pd_gr['Google評論分數_x'].values.sum()/pd_gr['Google評論分數_y'].values.sum()
for i in range(len(pd_gr.index)):
    pd_gr.iloc[i,3]=(pd_gr.iloc[i,1]/pd_gr.iloc[i,2])*100
avggrrate=pd_gr['評分率'].values.mean()
#by year
pd_yearcreated= pd_VMI.groupby('發照年YYYY')['機構名稱'].count()
pd_yearcreated=pd_yearcreated.drop('Unknown',axis=0)
#print(pd_yearcreated.index)



#畫圖: show 台灣目前合法獸醫醫療診所總數,每個縣市平均的寵物醫療診所數量,寵物醫療院所成立的時間軸
fig=plt.figure(figsize=(15,10),dpi=120,edgecolor='#37474F')
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
#圖一左上
ax1= plt.subplot2grid((6,9),(0,0),colspan=2)
ax1.set_xticks([]) # 不要顯示x軸刻度
ax1.set_yticks([]) # 不要顯示y軸刻度
ax1.set_title('全台已登記寵物數量',fontsize=14)
ax1.text(0.5,0.4,'%d'%(sumPet),fontsize=36,fontweight='heavy',c='#37474F',ha='center')
#ax1.set_facecolor('#37474F')
#圖二右上
ax2= plt.subplot2grid((6,9),(0,2),colspan=2)
ax2.set_xticks([]) # 不要顯示x軸刻度
ax2.set_yticks([]) # 不要顯示y軸刻度
ax2.set_title('平均各縣市登記隻數',fontsize=14)
ax2.text(0.5,0.4,'%.1f'%(sumPet/len(CountyReg.index)),fontsize=35,fontweight='heavy',c='#37474F',ha='center')
ax2.text(0.95,0.2,'隻',fontsize=18,fontweight='heavy',c='#37474F',ha='center')
#ax2.set_facecolor('#37474F')
#圖三左二
ax3= plt.subplot2grid((6,9),(1,0),colspan=2)
ax3.set_xticks([]) # 不要顯示x軸刻度
ax3.set_yticks([]) # 不要顯示y軸刻度
ax3.set_title('全台總登記戶數',fontsize=14)
ax3.text(0.5,0.4,'%d'%(sumHouse),fontsize=36,fontweight='heavy',c='#37474F',ha='center')
#圖四右二
ax4= plt.subplot2grid((6,9),(1,2),colspan=2)
ax4.set_xticks([]) # 不要顯示x軸刻度
ax4.set_yticks([]) # 不要顯示y軸刻度
ax4.set_title('平均各縣市登記戶數',fontsize=14)
ax4.text(0.5,0.4,'%.1f'%(sumHouse/len(CountyReg.index)),fontsize=35,fontweight='heavy',c='#37474F',ha='center')
ax4.text(0.95,0.2,'戶',fontsize=18,fontweight='heavy',c='#37474F',ha='center')
#圖五中
ax5= plt.subplot2grid((6,9),(2,1),colspan=2)
ax5.set_xticks([]) # 不要顯示x軸刻度
ax5.set_yticks([]) # 不要顯示y軸刻度
ax5.set_title('每戶平均登記隻數',fontsize=14)
ax5.text(0.5,0.4,'%.1f'%(sumPet/sumHouse),fontsize=36,fontweight='heavy',c='#37474F',ha='center')
ax5.text(0.8,0.3,'隻',fontsize=18,fontweight='heavy',c='#37474F',ha='center')
#圖六中下
ax6= plt.subplot2grid((6,9),(3,0),rowspan=3,colspan=4)
ax7 = ax6.twinx()
ax6.plot(CountyReg['登記縣市'].values,CountyReg['登記隻數'].values,lw=1.2,color="#616161")
ax6.set_ylim([0,max(CountyReg['登記隻數'].values)+50000])
ax6.set_xticklabels(CountyReg['登記縣市'].values,rotation=90,fontsize=12)
#ax6.axhline(sumPet/len(CountyReg.index), color='#37474F', lw=1.5, alpha=0.8,ls='--')
#ax6.text(CountyReg.index[-6],(sumPet/len(CountyReg.index))+500,"平均各縣市寵物登記數: %.1f"%(sumPet/len(CountyReg.index)),c='black',fontsize=11.5,fontweight="bold")
ax6.set_ylabel('登記總數量(隻)', color='#616161',fontsize=11.5)
ax6.tick_params(axis='y',labelcolor='#616161')
ax6.set_title('縣市分布概況',fontsize=15)
ax7.plot(CountyReg['登記縣市'].values,CountyReg['每戶平均登記數'].values,lw=1.2,color='#186a93ff') 
ax7.set_ylabel('平均登記數(隻/戶)', color='#186a93ff',fontsize=11.5)
ax7.set_ylim([0,max(CountyReg['每戶平均登記數'].values)+1])
ax7.tick_params(axis='y',labelcolor='#186a93ff')
#圖八底部
ax8= plt.subplot2grid((6,9),(1,4),rowspan=4,colspan=5)
ax8.scatter(CountyReg['登記隻數'].values,CountyReg['每戶平均登記數'].values,marker='^',c='#027dbbff')
ax8.set_xlabel("登記總數量(隻)",fontsize=11)
ax8.set_ylabel('平均登記數(隻/戶)',fontsize=11)
ax8.axvline(sumPet/len(CountyReg.index),c="#eea904ff",lw=1.2)
ax8.axhline(y=sumPet/sumHouse,c="#eea904ff",lw=1.2)
ax8.text(sumPet/len(CountyReg.index),sumPet/sumHouse,"Avg.\n(%.2f,%.2f)"%(sumPet/len(CountyReg.index),sumPet/sumHouse), ha="center", va="center",size=10.5,
    bbox=dict(boxstyle="circle,pad=0.3", fc="#fbc11cff", ec="#eea904ff", lw=0.5,alpha=0.6,))
ax8.set_title("各縣市 登記總數 v.s 每戶平均登記數",fontsize=15)

for i in range(len(CountyReg.index)):
    if CountyReg.iloc[i,2]>= (sumPet/len(CountyReg.index)):
        ax8.text(CountyReg.iloc[i,2],CountyReg.iloc[i,3]+0.03,CountyReg.iloc[i,0],fontsize=10.5,c='#027dbbff',fontweight='bold')

for ax, color in zip([ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8], ['white', 'white', 'white', 'white', 'white','white', 'white', 'white']):
    plt.setp(ax.spines.values(), color=color)
    plt.setp([ax.get_xticklines(), ax.get_yticklines()], color=color)

fig.suptitle('台灣寵物飼養登記概況',fontsize=20,fontweight='bold',y=1.05)
fig.tight_layout()
#plt.savefig('台灣寵物飼養登記概況.png',pad_inches=0.0)#pad_inches: 去除所有白邊
plt.show()




#畫圖: show 台灣目前合法獸醫醫療診所總數,每個縣市平均的寵物醫療診所數量,各縣市診所數量和登記數量的散步圖分布
fig=plt.figure(figsize=(15.5,10),dpi=120,edgecolor='#37474F')
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
plt.rcParams['axes.unicode_minus']=False #讓坐標軸可以顯示- 
#圖一左上
ax1= plt.subplot2grid((5,9),(0,0),colspan=2)
ax1.set_xticks([]) # 不要顯示x軸刻度
ax1.set_yticks([]) # 不要顯示y軸刻度
ax1.set_title('合法獸醫醫療診所總數',fontsize=14)
ax1.text(0.5,0.4,'%d'%(clincs_num),fontsize=36,fontweight='heavy',c='#37474F',ha='center')
#ax1.set_facecolor('#37474F')
#圖二右上
ax2= plt.subplot2grid((5,9),(0,2),colspan=2)
ax2.set_xticks([]) # 不要顯示x軸刻度
ax2.set_yticks([]) # 不要顯示y軸刻度
ax2.set_title('平均各縣市獸醫院所數量',fontsize=14)
ax2.text(0.5,0.4,'%.1f'%(clincs_num/len(pd_vetclinccity.index)),fontsize=36,fontweight='heavy',c='#37474F',ha='center')
ax2.text(0.95,0.3,'間',fontsize=20,fontweight='heavy',c='#37474F',ha='center')
#ax2.set_facecolor('#37474F')
#圖三中間
ax3= plt.subplot2grid((5,9),(1,1),colspan=2)
ax3.set_xticks([]) # 不要顯示x軸刻度
ax3.set_yticks([]) # 不要顯示y軸刻度
ax3.text(0.5,0.4,'%.1f'%(sum(pd_pet['登記隻數'].values)/clincs_num),fontsize=36,fontweight='heavy',c='#37474F',ha='center')
ax3.text(0.95,0.3,'隻',fontsize=20,fontweight='heavy',c='#37474F',ha='center')
ax3.set_title('獸醫院所平均負載量',fontsize=14)
#圖四底部
ax4= plt.subplot2grid((5,9),(2,0),rowspan=3,colspan=4)
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
#圖五右半部
ax5= plt.subplot2grid((5,9),(0,4),rowspan=5,colspan=5)
ax5.scatter(pd_pet['機構數量'].values,pd_pet['平均各機構負載'].values,marker='^',c='#06aab6ff')
ax5.axvline(clincs_num/len(pd_vetclinccity.index),c="#eea904ff",lw=1.2)
ax5.axhline(y=sum(pd_pet['登記隻數'].values)/clincs_num,c="#eea904ff",lw=1.2)
ax5.set_xlabel('獸醫診所數量',fontsize=12)
ax5.set_ylabel('平均負載量(隻/間)',fontsize=12)
ax5.set_ylim([-1000,max(pd_pet['平均各機構負載'].values)+200])
ax5.set_title('各縣市獸醫院所數量與負載量關係',fontsize=14)
for i in range(len(pd_pet.index)):
    if (pd_pet.iloc[i,0]>= (clincs_num/len(pd_vetclinccity.index)))and (pd_pet.iloc[i,1]>=(sum(pd_pet['登記隻數'].values)/clincs_num)):
        ax5.text(pd_pet.iloc[i,0],pd_pet.iloc[i,1]+30,pd_pet.iloc[i,2],fontsize=11.5,c='#06aab6ff',rotation=60)
    elif (pd_pet.iloc[i,0]< (clincs_num/len(pd_vetclinccity.index)))and (pd_pet.iloc[i,1]>=((sum(pd_pet['登記隻數'].values)/clincs_num)*2)):
        ax5.text(pd_pet.iloc[i,0],pd_pet.iloc[i,1]+30,pd_pet.iloc[i,2],fontsize=11.5,c='#06aab6ff')
    elif pd_pet.iloc[i,0]==0:
        ax5.text(pd_pet.iloc[i,0],pd_pet.iloc[i,1]+30,pd_pet.iloc[i,2],fontsize=11.5,c='#06aab6ff',rotation=60)
ax5.text(clincs_num/len(pd_vetclinccity.index),(sum(pd_pet['登記隻數'].values)/clincs_num)+30,'Average:\n(%.1f,%.1f)'%(clincs_num/len(pd_vetclinccity.index),sum(pd_pet['登記隻數'].values)/clincs_num),fontsize=11.5,c='black',va='center',ha='center')
for ax, color in zip([ax1, ax2, ax3, ax4, ax5], ['white', 'white', 'white', 'white', 'white']):
    plt.setp(ax.spines.values(), color=color)
    plt.setp([ax.get_xticklines(), ax.get_yticklines()], color=color)
fig.suptitle('台灣獸醫院所資源概況',fontsize=20,fontweight='bold',y=1.05)
fig.tight_layout()
plt.savefig('台灣獸醫院所資源概況.png',pad_inches=0.0)#pad_inches: 去除所有白邊
plt.show()


#畫圖: Google Review Score
fig=plt.figure(figsize=(15,10),dpi=120,edgecolor='#37474F')
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
#圖一左上
ax1= plt.subplot2grid((4,8),(0,0),colspan=2)
ax1.set_xticks([]) # 不要顯示x軸刻度
ax1.set_yticks([]) # 不要顯示y軸刻度
ax1.text(0.5,0.5,'%.2f'%avggr,fontsize=36,fontweight='bold',c='#37474F',ha='center')
ax1.set_title('Google評論分數平均',fontsize=14)
#圖二左上二
ax2= plt.subplot2grid((4,8),(0,2),colspan=2)
ax2.set_xticks([]) # 不要顯示x軸刻度
ax2.set_yticks([]) # 不要顯示y軸刻度
ax2.text(0.5,0.5,'%d'%count_rate,fontsize=36,fontweight='bold',c='#37474F',ha='center')
ax2.text(0.8,0.3,'間',fontsize=20,fontweight='bold',c='#37474F',ha='center')
ax2.set_title('被評價獸醫院所數量',fontsize=14)
#圖三左下
ax3= plt.subplot2grid((4,8),(1,0),rowspan=3,colspan=4)
ax3.scatter(pd_gr['平均評分'].values,pd_gr['評分率'].values,marker='^',c='#06aab6ff')
ax3.set_xlabel('Google評論分數平均',fontsize=11.5)
ax3.set_ylabel('評分率(%)',fontsize=11.5)
ax3.axvline(avggr,c="#eea904ff",lw=1.2)
ax3.axhline(y=avggrrate,c="#eea904ff",lw=1.2)
ax3.set_title('各縣市 Google評分概況',fontsize=15)
for i in range(len(pd_gr.index)):
    if pd_gr.iloc[i,4]<avggr:
        ax3.text(pd_gr.iloc[i,4],pd_gr.iloc[i,3]+1,pd_gr.index[i],fontsize=11,c='#027dbbff',rotation=90)
#圖四右
ax4= plt.subplot2grid((4,8),(0,4),rowspan=4,colspan=4)
ax4=sns.heatmap(review_table, fmt='d', linewidths=.6, cmap='GnBu',center=125,annot=True)
plt.setp(ax4.get_xticklabels(), rotation=90, ha="right",
         rotation_mode="anchor")
ax4.set_title('各縣市評價分布區間',fontsize=14)

for ax, color in zip([ax1, ax2, ax3, ax5], ['white', 'white', 'white','white']):
    plt.setp(ax.spines.values(), color=color)
    plt.setp([ax.get_xticklines(), ax.get_yticklines()], color=color)
fig.suptitle('台灣獸醫院所評分一覽',fontsize=20,fontweight='bold',y=1.05)
fig.tight_layout()
plt.savefig('台灣獸醫院所評論分數.png')
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

pd_vetclinccity = pd.merge(pd_vetclinccity,pd_gr,left_on = '機構縣市',right_index = True,how='outer')
# define the national map
national_map = folium.Map(location=[23.9005,120.5995],tiles='cartodbpositron',zoom_start=7,width='100%',height='100%')
colors=['red','yellow','lime','silver']
for lat, lng, label, city, rc, rr in zip(pd_vetclinccity['緯度'].values, pd_vetclinccity['經度'].values, pd_vetclinccity['機構名稱'].values,pd_vetclinccity['機構縣市'].values,pd_vetclinccity['平均評分'].values,pd_vetclinccity['評分率'].values):
    html = '<h3>'+city+'</h3><br>合法獸醫院所: %.0f間<br>評論分數平均: %.1f分<br>評分率:%.1f%%'%(label,rc,rr)
    iframe = folium.IFrame(html)
    popup = folium.Popup(iframe,
                     min_width=240,max_width=240)
    if label!=0.0:
        radius=math.log(label,4)*5
        if (rc>=avggr)and(rr>=avggrrate):
            folium.CircleMarker(location=[lat, lng],radius=radius,
                                fill=True,fill_opacity=0.7,
                                color=colors[2],opacity=0.9,
                                fill_color=colors[2],
                                popup=popup,
                                #popup="%s\n合法獸醫院所: %d 間"%(city,label),
                                ).add_to(national_map)
        elif (rc>=avggr)and(rr<avggrrate):
            folium.CircleMarker(location=[lat, lng],radius=radius,
                                fill=True,fill_opacity=0.7,
                                color=colors[3],opacity=0.9,
                                fill_color=colors[3],
                                popup=popup,
                                #popup="%s\n合法獸醫院所: %d 間"%(city,label),
                                ).add_to(national_map)
        elif (rc<avggr)and(rr<avggrrate):
            folium.CircleMarker(location=[lat, lng],radius=radius,
                                fill=True,fill_opacity=0.7,
                                color=colors[1],opacity=0.9,
                                fill_color=colors[1],
                                popup=popup,
                                #popup="%s\n合法獸醫院所: %d 間"%(city,label),
                                ).add_to(national_map)
        elif (rc<avggr)and(rr>=avggrrate):
            folium.CircleMarker(location=[lat, lng],radius=radius,
                                fill=True,fill_opacity=0.7,
                                color=colors[0],opacity=0.9,
                                fill_color=colors[0],
                                popup=popup,
                                #popup="%s\n合法獸醫院所: %d 間"%(city,label),
                                ).add_to(national_map)
    else:
        radius=2.5
        folium.CircleMarker(location=[lat, lng],radius=radius,
                            fill=True,fill_opacity=0.7,
                            color=colors[0],opacity=0.9,
                            fill_color=colors[0],
                            popup=popup,
                            #popup="%s\n合法獸醫院所: %d 間"%(city,label),
                            ).add_to(national_map)

national_map.save('map_pet_medical_service.html')