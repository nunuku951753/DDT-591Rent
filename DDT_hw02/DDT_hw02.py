#!/usr/bin/env python
# coding: utf-8

import requests
from bs4 import BeautifulSoup
import pymongo
from pprint import pprint
import re

# DB連線
def connectDB():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["mydb"]
    mycoll = mydb["rent"]
#     db_list = myclient.list_database_names() #查看已存在DB
#     coll_list = mydb.list_collection_names() #查看已存在資料集
    return mycoll

# 轉換性別
def getGender(name):
    male = ["先生", "男士", "爸爸"]
    female = ["小姐", "太太", "女士", "媽媽"]
    gender = "unknown"
    if any( e in name for e in male):
        gender = "M"
    elif any( e in name for e in female):
        gender = "F"
    return gender

# 轉換成小時數
def getHours(time):
    hour = 0
    if "天" in time:
        hour = int(re.findall(r"[0-9]+", time)[0]) * 24
    elif "小時" in time:
        hour = int(re.findall(r"[0-9]+", time)[0])
    elif "分鐘" in time:
        hour = round(int(re.findall(r"[0-9]+", time)[0]) / 60, 2)
    return hour

# update_freq = 幾小時內資料要更新
def crawler(citys, update_freq):
    conn = connectDB() # mongodb
    url = "https://rent.591.com.tw/"
    for city in citys:
        print("city:", citys[city])

        page = 0
        keepWhile = True
        while keepWhile:
            print("page =", (page+1))
            rent_arr = []
            header={
                "Cookie" : "urlJumpIp=" + city
            }
            params = dict(
                firstRow = page * 30
            )

            result = requests.get(url, headers=header, params=params)
            list_page = BeautifulSoup(result.text, 'html.parser')
            total = list_page.find("div", class_="pull-left hasData").find("i").text
            uls = list_page.findAll("ul", class_="listInfo clearfix")
#             print("total =", total)

            for ul in uls:
                rent_dict = {}

                # 刪除指定區塊
                ul.find("p", class_="lightBox").decompose()
                ul.find("p", class_="lightBox").decompose()
                updatetime = ul.find("p").text.replace(" ", "").split("/")[1]
                hour = getHours(updatetime)
                # 判斷是否結束程式
                if hour > update_freq:
                    keepWhile = False # 結束程式
                    print("updatetime out of range, break while loop!", hour, "/ hour")
                    break

                detail_url = "http:" + ul.find("a")['href']
                detail_page = BeautifulSoup(requests.get(detail_url).text, 'html.parser')

                address = detail_page.find("span", class_="addr").text
                owner = detail_page.find("div", class_="avatarRight").text                                    .replace("（", "(").replace("）", ")").replace("\n", "")
                phone = detail_page.find("span", class_="dialPhoneNum")['data-value']

                rent_dict['web_link'] = detail_url
                rent_dict['city'] = citys[city]
                rent_dict['address'] = address
                rent_dict['owner'] = owner[: owner.index("(")]
                rent_dict['identity'] = owner[owner.index("(")+1 : owner.index(")")]
                rent_dict['gender'] = getGender(owner[: owner.index("(")])
                rent_dict['phone'] = phone

                info_div = detail_page.find("div", class_="detailInfo clearfix")
                price = info_div.find("div", class_="price clearfix").find("i").text
                rent_dict['price'] = price
                info_lis = info_div.find("ul", class_="attr").findAll("li")
                for li in info_lis:
                    key = li.text[:li.text.index(":")].strip()
                    value = li.text[li.text.index(":")+1:].strip()
                    rent_dict[key] = value

                # clearfix item
                clearfix_ul = detail_page.find("ul", class_="clearfix labelList labelList-1")
                one_divs = clearfix_ul.findAll("div", class_="one") # title
                two_divs = clearfix_ul.findAll("div", class_="two") # value
                for i, div in enumerate(one_divs):
                    key = div.text
                    value = two_divs[i].text.replace("：", "").replace(":", "").strip()
                    rent_dict[key] = value

                rent_arr.append(rent_dict)

            if rent_arr != []:
                conn.insert_many(rent_arr)
            page += 1
    #     break # city break


# main flow
citys = {"1" : "台北市", "3" : "新北市"}
update_freq = 0.5 # 幾小時內資料要更新

crawler(citys, update_freq)

