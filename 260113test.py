#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#conda create -n testenv python=3.11
#conda activate testenv
#pip install numpy pandas matplotlib requests selenium lxml


# In[25]:


# 题目1
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import io
import os
import time

def fetch_bonds_by_text_navigation():
    chrome_options = Options()
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get("https://www.chinamoney.com.cn/english/bdInfo/")
        
        time.sleep(10) 
    
        js_interaction = """
        function interactByText() {
            let allSelects = document.querySelectorAll('select');
            for(let s of allSelects) {
                if(s.innerHTML.includes('Treasury')) s.value = '1';
                if(s.innerHTML.includes('2023')) s.value = '2023';
            }
            
            let allBtns = document.querySelectorAll('a, button, span');
            for(let b of allBtns) {
                if(b.innerText.trim() === 'Search') {
                    b.click();
                    return true;
                }
            }
            return false;
        }
        return interactByText();
        """
        
        driver.execute_script(js_interaction)
        time.sleep(12) 
        
        all_html = [driver.page_source]
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for i in range(len(iframes)):
            try:
                driver.switch_to.frame(i)
                all_html.append(driver.page_source)
                driver.switch_to.default_content()
            except: continue

        for html in all_html:
            try:
                dfs = pd.read_html(io.StringIO(html))
                for df in dfs:
                    if len(df.columns) >= 6 and not df.empty:
                       
                        res = df.iloc[:, [0, 1, 2, 3, 4, 8 if len(df.columns)>8 else -1]]
                        res.columns = ["ISIN", "Bond Code", "Issuer", "Bond Type", "Issue Date", "Latest Rating"]
                        
                        path = "D:\\260113test\Treasury_Bonds_2023.csv"
                        res.to_csv(path, index=False, encoding='utf-8-sig')
                        print(f"数据已导出至: {path}")
                        return
            except: continue


    except Exception as e:
        print(f"运行中断: {e}")
    finally:
        time.sleep(30) 
        driver.quit()

if __name__ == "__main__":
    fetch_bonds_by_text_navigation()


# In[24]:


# 题目2
import re

def reg_search(text, regex_list):
    results = []
    
    clean_text = "".join(text.split())
    
    for regex_item in regex_list:
        match_entry = {}
        for key, pattern in regex_item.items():

            matches = re.findall(pattern, clean_text)
            
            if not matches:
                match_entry[key] = None
                continue
            
            if key == '换股期限':
                
                date_results = []
                for m in matches:
                    
                    formatted = re.sub(r'(\d+)年(\d+)月(\d+)日', 
                                       lambda x: f"{x.group(1)}-{x.group(2).zfill(2)}-{x.group(3).zfill(2)}", 
                                       m)
                    date_results.append(formatted)
                match_entry[key] = date_results
            else:
                match_entry[key] = matches[0]
                
        results.append(match_entry)
    
    return results

#  测试代码 
text = '''
标的证券：本期发行的证券为可交换为发行人所持中国长江电力股份
有限公司股票（股票代码：600900.SH，股票简称：长江电力）的可交换公司债
券。
换股期限：本期可交换公司债券换股期限自可交换公司债券发行结束
之日满 12 个月后的第一个交易日起至可交换债券到期日止，即 2023 年 6 月 2
日至 2027 年 6 月 1 日止。
'''

custom_regex_list = [{
    '标的证券': r'\d{6}\.[A-Z]{2}',
    '换股期限': r'\d{4}年\d{1,2}月\d{1,2}日'
}]

output = reg_search(text, custom_regex_list)
print(output)

