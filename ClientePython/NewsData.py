from newsdataapi import NewsDataApiClient
import dateutil
import json
import pandas as pd
from transformers import pipeline
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from datetime import date
from elasticsearch import helpers
from elasticsearch import Elasticsearch

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
                'keyword1': [],
                'keyword2': [],
                'keyword3': [],
                'link':[],
                'resume':[],
                'source':[],
                'artiClus':[],
                'resuClus':[]
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
            self.parseData(response)
        self.dataToCsv()



    def parseData(self,articles):

        articles=articles["results"]
        for article in articles:
            content=article["content"]
            date=dateutil.parser.parse(article['pubDate']).date()
            keyw=article["keywords"]
            k0=self.getKeyword(keyw,0)
            k1 = self.getKeyword(keyw, 1)
            k2 = self.getKeyword(keyw, 2)

            if content and date:
                self.data["title"].append(article["title"])
                self.data["date"].append(date)
                self.data["description"].append(article["description"])
                self.data["content"].append(content)
                self.data["keyword1"].append(k0)
                self.data["keyword2"].append(k1)
                self.data["keyword3"].append(k2)
                self.data["link"].append(article["link"])
                self.data["resume"].append(self.summarize(content))
                self.data["source"].append(article["source_id"])
                self.data["artiClus"].append(None)
                self.data["resuClus"].append(None)


        return  pd.DataFrame(self.data)

    def getKeyword(self,v, i):
        if v:
            if len(v) > i:
                #print( v[i])
                return v[i]
            else:
                return None





    def dataToCsv(self):
        dt=pd.DataFrame(self.data)
        dt.to_csv("todayNews.csv")

    def summarize(self,text):
        generator = pipeline("summarization", model="google/pegasus-xsum")
        res = generator(text, temperature=0.3, truncation=True)
        return res[0]['summary_text']


def getKeyword(vec,i):
    list=[]
    print(vec)
    for j in range(len(vec)):
        if type(vec[j])!=float:
            text=vec[j].replace("[","")
            text=text.replace("]","")
            text = text.replace("'", "")
            v=text.split(",")

            if len(v)>i:
                list.append(v[i])
            else:
                list.append(None)
        else:list.append(None)

    return list

def actualizarCSV():
    csv=pd.read_csv("todayNews.csv", index_col=0)
    n=[None]*(len(csv))
    new={
        'title':csv["title"],
        'date': csv["date"],
        'description': csv["description"],
        'content': csv["content"],
        'keyword1': getKeyword(csv["keyword1"],0),
        'keyword2': getKeyword(csv["keyword1"],1),
        'keyword3': getKeyword(csv["keyword1"],2),
        'link': csv["link"],
        'resume': csv["resume"],
        'source': csv["source"],
        'artiClus': n,
        'resuClus': n
    }
    pd.DataFrame(new).to_csv("basura/news05N.csv")
def combinarCsv():
    file=open("todayNews.csv", encoding="utf8")
    file2 = open("NEWSACT.csv", encoding="utf8")
    csv=pd.read_csv(file)
    csv2 = pd.read_csv(file2)
    frames=[csv,csv2]
    fi=pd.concat(frames,ignore_index=True)
    del fi['Unnamed: 0']
    fi.to_csv("NEWSACT.csv")


def cambiarDelimiter():
    file = open("basura/newsN.csv", encoding="utf8")
    csv= pd.read_csv(file)
    del csv["Unnamed: 0"]
    csv.to_csv("newsN2.csv",sep = '|')

def resumirTodo():
    file = open("basura/newsN.csv", encoding="utf8")
    csv= pd.read_csv(file)
    del csv["Unnamed: 0"]
    #for i in csv.index:

    la=len(csv)
    for i in range(la):
        print("Instancia: "+str(i)+"/"+str(la))
        re = csv["content"][i]
        csv.loc[i,"resume"]=summarize(re)

    csv.to_csv("newsNResumido.csv")



def summarize(text):
    generator = pipeline("summarization", model="google/pegasus-xsum")
    res = generator(text, temperature=0.3, truncation=True)
    return res[0]['summary_text']

def KMeansClustering(dataVec):
    data=tfidf(dataVec,200)
    cluster=KMeans(init="k-means++", n_clusters=11)
    cluster.fit_predict(data)

    #print(cluster.labels_)
    return cluster.labels_

def tfidf(df,maxfeatures):
    tfidfvectorizer = TfidfVectorizer(analyzer='word',stop_words= 'english',max_features=maxfeatures)# convert th documents into a matrix
    tfidf_wm = tfidfvectorizer.fit_transform(df)#retrieve the terms found in the corpora
    tfidf_tokens = tfidfvectorizer.get_feature_names()
    ind=[]
    for i in range(len(df)):ind.append(i)
    df_tfidfvect = pd.DataFrame(data = tfidf_wm.toarray(),index =ind,columns = tfidf_tokens)
    #normalice data
    sc=StandardScaler()
    df_scaled=pd.DataFrame(sc.fit_transform(df_tfidfvect), columns = tfidf_tokens)
    return(df_scaled)

def saveClusters(data,artiClus,resuClus):
    for i in range(len(data)):
        data.loc[i,"artiClus"]=artiClus[i]
        data.loc[i, "resuClus"] = resuClus[i]

    data.to_csv("NEWSACT.csv")

def putDatos(indexName):
    config = {
        'host': 'http://35.195.149.133:9200'
    }
    es = Elasticsearch(['http://35.195.149.133'])
    actions=[]
    data=pd.read_csv("NEWSACT.csv")
    for index,row in data.iterrows():
        print()
        action={
            "_index": indexName,
            "_source": {
                "title":row["title"],
                "date": row["date"],
                "description": row["description"],
                "content": row["content"],
                "keyword1": row["keyword1"],
                "keyword2": row["keyword2"],
                "keyword3": row["keyword3"],
                "link": row["link"],
                "resume": row["resume"],
                "source": row["source"],
                "artiClus": row["artiClus"],
                "resuClus": row["resuClus"]}}
        actions.append(action)

    helpers.bulk(es, actions)

if __name__ == '__main__':
    #GET TODAY NEWS
    nApi= NewsApi()
    nApi.getLastestNews(50)
    combinarCsv()
    #CLUSTERING
    data = pd.read_csv("NEWSACT.csv", index_col=0)
    articulos = data["content"]
    resumenes = data["resume"]
    artiCLus = KMeansClustering(articulos)
    resuCLus = KMeansClustering(articulos)
    saveClusters(data, artiCLus, resuCLus)
    #SUBIR A ELASTIC SEARCH
    today = str(date.today())
    putDatos(date.today())







# News API

