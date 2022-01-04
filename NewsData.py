from newsdataapi import NewsDataApiClient
import datetime
import dateutil
from dateutil.relativedelta import relativedelta
import json
import pandas as pd
from openpyxl.workbook import Workbook



class NewsApi:
    def __init__(self):

        with open("keys.json") as file:
            self.jsonKeys = json.load(file)
        self.apiKeyIn =self.jsonKeys["using"]
        self.keys=self.jsonKeys["list"]

        self.data= {
                'title': [],
                'date': [],
                'description': [],
                'content': [],
                'keywords': [],
                'link':[],
                'resume':[],
                'source':[]
                }


    def getKey(self):
        apiK=self.keys[self.apiKeyIn]["key"]
        return apiK

    def changeKey(self):
        self.apiKeyIn += 1
        self.jsonKeys["using"]=self.apiKeyIn
        with open('keys.json', 'w') as file:
            json.dump(self.jsonKeys, file, indent=4)


    def getLastestNews(self,pages):
        api=NewsDataApiClient(apikey=self.getKey())
        for i in range(pages):
            response = api.news_api(language="en",page=i)
            if response["status"]!="success":
                self.changeKey()
                api = NewsDataApiClient(apikey=self.getKey())
                response = api.news_api(language="en", page=i)
           # self.saveData(response,i)
            self.parseData(response)
        self.dataToCsv()



    def parseData(self,articles):

        articles=articles["results"]
        for article in articles:
            content=article["content"]
            date=dateutil.parser.parse(article['pubDate']).date()

            if content and date:
                self.data["title"].append(article["title"])
                self.data["date"].append(date)
                self.data["description"].append(article["description"])
                self.data["content"].append(content)
                self.data["keywords"].append(article["keywords"])
                self.data["link"].append(article["link"])
                self.data["resume"].append(None)
                self.data["source"].append(article["source_id"])


        return  pd.DataFrame(self.data)

    def dataToCsv(self):
        dt=pd.DataFrame(self.data)
        dt.to_csv("news2.csv")
        dt.to_excel("news2.xlsx")

    def summarize(self,text):


    def saveData(self,data,loop):
        with open('data' + str(loop) + '.json', 'w') as file:
            json.dump(data, file, indent=4)


def cargarCsv():
    file=open("news.csv",encoding="utf8")
    file2 = open("news2.csv",encoding="utf8")
    csv=pd.read_csv(file)
    csv2 = pd.read_csv(file2)
    frames=[csv2,csv]
    fi=pd.concat(frames,ignore_index=True)


    del fi['Unnamed: 0']

    fi.to_csv("newsN.csv")
    fi.to_csv("newsN.xlsx")
    fi.to_json("newsN.json")



if __name__ == '__main__':
    nApi= NewsApi()

    #pt=nApi.parseData(js)
    #nApi.dataToCsv(pt)
    #nApi.getLastestNews(50)

    nApi.getLastestNews(1)



# News API

