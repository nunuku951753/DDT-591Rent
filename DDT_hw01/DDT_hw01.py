#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import xml.etree.ElementTree as etree


math_map = { "零" : 0, "一" : 1, "二" : 2, "三" : 3, "四" : 4, "五" : 5,
             "六" : 6, "七" : 7, "八" : 8, "九" : 9, "十" : 10, "層" : 0 }

# 讀取xml
def getLandDF(filename):
    tree = etree.parse("data/" + filename)
    root = tree.getroot()

    columns = [elem.tag for elem in root[0].iter() if elem is not root[0]]
    datatframe = pd.DataFrame(columns = columns)

    for node in root:
        data_arr = []
        for elem in node.iter():
            content = ""
            if elem is not node:
                try:
                    content = node.find(elem.tag).text
                except:
                    content = ""
                data_arr.append(content)

        datatframe = datatframe.append(pd.Series(data_arr, index = columns), ignore_index = True)
    return datatframe

# 百樓以下數字轉換
def getMath(floor): 
    math = 0
    for f in floor:
        num = math_map[f]
        if num == 10:
            if math==0:
                math = 1
            math = math * num
        else:
            math += num
    return math

# 樓層數字轉換
def getFloor(floor):
    if floor is None:
        return 0
    if "百" in floor:
        f_sp = floor.split("百")
        math = math_map[f_sp[0]] * 100 + getMath(f_sp[1])
    else:
        math = getMath(floor)
    return math

# 擷取車位數
def getParking(text):
    parking = ""
    if "車位" in text:
        parking = text[text.index('車位')+2:]
    else:
        parking = "0"
    return int(parking)


# In[2]:


def getAllData():
    df_a = getLandDF("a_lvr_land_a.xml")
    df_b = getLandDF("b_lvr_land_a.xml")
    df_e = getLandDF("e_lvr_land_a.xml")
    df_f = getLandDF("f_lvr_land_a.xml")
    df_h = getLandDF("h_lvr_land_a.xml")

    all_df = pd.DataFrame([])
    all_df = all_df.append(df_a).append(df_b).append(df_e).append(df_f).append(df_h)

    all_df["floor"] = all_df["總樓層數"].apply(lambda x: getFloor(x))
    all_df["parking"] = all_df["交易筆棟數"].apply(lambda x: getParking(x))
    all_df['parking_price'] = all_df["車位移轉總面積平方公尺"].apply(pd.to_numeric, errors='ignore') *                               all_df["單價元平方公尺"].apply(pd.to_numeric, errors='ignore')

    print(df_a.shape, df_b.shape, df_e.shape, df_f.shape, df_h.shape)
    print(all_df.shape)
    return all_df


# In[4]:


def getFilterA(all_df):
    final_df = all_df.loc[(all_df["主要用途"] == "住家用") 
                            & (all_df["建物型態"].str.contains("住宅大樓"))
                            & (all_df["floor"] >= 13)]

    final_df.to_csv('./filter_a.csv', index = False, header = True)
    
def getFilterB(all_df):
    num = len(all_df)
    total = all_df["總價元"].apply(pd.to_numeric, errors='ignore').sum(axis = 0, skipna = True)
    parking_num = all_df["parking"].apply(pd.to_numeric, errors='ignore').sum(axis = 0, skipna = True)
    parking_total = all_df["parking_price"].apply(pd.to_numeric, errors='ignore').sum(axis = 0, skipna = True)

    columns = ["總件數", "總車位數", "平均總價元", "平均車位總價元"]
    datas = [num, parking_num, (total/num), (parking_total/parking_num)]

    final_df2 = pd.DataFrame([], columns = columns)
    final_df2 = final_df2.append(pd.Series(datas, index = columns), ignore_index = True)

    final_df2.to_csv('./filter_b.csv', index = False, header = True)


# In[ ]:


all_df = getAllData()
getFilterA(all_df)
getFilterB(all_df)

