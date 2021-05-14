# -*- coding: utf-8 -*-
import requests as rq
import pandas as pd
from bs4 import BeautifulSoup
# data collection :web crawler/ json file / api 
# linktype: 'wb'(website) 'json'(api file with json or all json file)
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


# data cleaning :html tag name
def webcrawler(search_key,tagname,classname,indexnum):
    url='https://www.google.com/search?q='+search_key+'&authuser=1&sxsrf=ALeKk03cgwLYEBNl8oVOkOP7VGVt1j5QKw%3A1619967550156&ei=Pr6OYMGNCa-xmAWmsaHYAg&oq='+search_key+'&gs_lcp=Cgdnd3Mtd2l6EAMyAggAMgIIJjoHCCMQsAMQJzoHCAAQRxCwAzoGCAAQBxAeOggIABAIEAcQHjoECCMQJzoECAAQQzoFCAAQzQJQ7rYBWMrVAWDC2AFoAXACeACAAUWIAZcEkgEBOZgBAKABAaoBB2d3cy13aXrIAQnAAQE&sclient=gws-wiz&ved=0ahUKEwjBpP-yoavwAhWvGKYKHaZYCCsQ4dUDCA4&uact=5'
    rs= rqResponse(url,linktype='wb')
    bsObj= BeautifulSoup(rs,'lxml')
    listbsObj=bsObj.find_all(tagname,{"class":classname})
    if len(listbsObj) >=1:
        return listbsObj[indexnum].text
    else:
        return "No Result"
    
# data cleaning :pandas
# incol is a list and each element is a dic:{col_name:[index,"default value"]}
# dropna= fill in True/only subset null[columns] or False
# dropdupli= [subset,inplace],dropdupli[0] is the subset to distiguish if it has duplicates,dropdupli[1] is inplace is True or False
# fillna= fill in number or False
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