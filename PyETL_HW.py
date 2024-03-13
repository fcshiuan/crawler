import os
import requests
from bs4 import BeautifulSoup

# 建立裝文章的資料夾
folderName = "PTT_Article"
if not os.path.exists(folderName) : os.mkdir(folderName) # 建立目錄


# 拜訪網頁時，我們自身的資訊(eg.作業系統、瀏覽器) p.圖HEADERS
HEADERS = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}
# 第一次造訪網頁，會詢問是否滿18，是的話會將我們加上cookies over18:1 p.圖COOKIES
COOKIES = {"over18":"1"}


# 爬取萃取文章內容
def article_content(url:str) ->str :

    # 向WebServer請求拜訪網頁，模仿人造訪網頁 p.8 p.9
    res = requests.get(url=url,headers=HEADERS,cookies=COOKIES)
    # 建立BeautifulSoup物件  將res.text的空白格式移除  "html.parser"使內容更乾淨，只留下標籤內容，<script>等會移除
    soup = BeautifulSoup(res.text,'html.parser') 
    
    # 取得主要文章區塊
    ArtMainCont =  soup.select_one('#main-content')

    # 取標頭- 作者、看板、標題、時間
    tags = ArtMainCont.select('span.article-meta-tag')
    values = ArtMainCont.select('span.article-meta-value')
    headLine = ''
    for i in range(len(tags)) :
        headLine += f'{tags[i].text}{values[i].text} '

    # 推噓數  'span.hl push-tag'
    pn = 0
    shn = 0
    for t in ArtMainCont.select('span.hl.push-tag'):
        ft = (t.text).strip()
        if ft == '推' : pn += 1
        elif ft == '噓' : shn += 1
    pushText = f'推: {pn}\n噓: {shn}\n分數: {pn-shn}'

    # 取內文-去除不要的   
    for tag in ('div','span'):
        for subtag in ArtMainCont.select(tag):
            subtag.extract()

    # 取作者: 標題: 時間:
    Info = ''
    for i in (0,2,3) :
        Info += f'{tags[i].text}:{values[i].text}\n'

    # 回傳內容
    return f"{headLine}\n{ArtMainCont.text}\n----split----\n{pushText}\n{Info}"
    


def main():

    # 旅遊版 最新頁
    url = "https://www.ptt.cc/bbs/Japan_Travel/index.html"

    # 爬取本版 2頁
    for _ in range(2):
        
        # 向WebServer請求拜訪網頁，模仿人造訪網頁 p.8 p.9
        res = requests.get(url=url,headers=HEADERS,cookies=COOKIES)
        # 建立BeautifulSoup物件  將res.text的空白格式移除  "html.parser"使內容更乾淨，只留下標籤內容，<script>等會移除
        soup = BeautifulSoup(res.text,'html.parser') 

        # 爬取文章標題及連結 (p.圖)
        articleTitleList = soup.select("div.title a") # -> list
        # 將list內項目一一取出
        for articleTitle in articleTitleList:
            # 文章內容網址 (p.圖) 
            ArticleContentUrl = "https://www.ptt.cc" + articleTitle['href']

            # 用標題為txt檔命名
            fileName = articleTitle.text 

            # try except 執行錯誤處理機制
            try:
                # open() 打開文件最後須伴隨close()關閉文件 ，with 區塊執行完自動關閉無須呼叫close()
                with open(f'{folderName}/{fileName}.txt','w', encoding="utf-8") as f :  
                    # 寫入內容 呼叫函式article_content(文章內容網址)
                    f.write(article_content(ArticleContentUrl))
            except FileNotFoundError : # 打開不存在的文件 的 錯誤
                fileName = fileName.replace('/','_') # 修正方式 檔名中'/'用'_'取代
                with open(f'{folderName}/{fileName}.txt','w', encoding="utf-8") as f :  
                    f.write(article_content(ArticleContentUrl))
            except OSError : pass
            except Exception as err : print(err)


        # 下一頁 (p.圖下一頁) "." class(btn與wide都是class) , "#" id  
        # soup.select("a.btn.wide") -> list  ,  list[1] index為1的
        url = "https://www.ptt.cc" + soup.select("a.btn.wide")[1]['href']
        


main()