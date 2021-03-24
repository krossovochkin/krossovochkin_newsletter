import requests
import urllib
import sys
import json
import telegram
from datetime import datetime, timedelta
import time
import os.path
    
def readSince():
    since = int(time.mktime((datetime.now() - timedelta(1)).timetuple()))

    file_name = "temp"
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            since = int(f.readline()) + 1
            
    return since
            
def saveSince(since):
    file_name = "temp"
    with open(file_name, "w") as f:
        f.write(str(since))
            
def loadArticles(since, single):
    url = f'https://getpocket.com/v3/get?consumer_key={consumer_key}&access_token={access_token}&state=archive&detailType=complete&since={since}&sort=oldest&tag=newsletter'
    
    if single:
        url += "&count=1"

    return json.loads(requests.get(url).content)
    
def mapArticles(data):
    items = list(map(lambda kv: kv[1], data["list"].items()))
    items = list(map(lambda x: mapArticle(x), items))
    return items
    
def mapArticle(item):
    title = item['given_title']
    url = item['resolved_url']
    description = item['excerpt']
    authors = ",".join(list(map(lambda kv: kv[1]['name'], item.get("authors", {}).items())))
    time_updated = item['time_updated']
    
    result = ""
    if authors:
        result +=  f"✍️ {authors}\n"
    
    result += f"🏷️ [{title}]({url})"
    
    if description:
        result += f"\n📜 {description}"
        
    return (result, time_updated)

if __name__ == "__main__":
    consumer_key = sys.argv[1]
    access_token = sys.argv[2]
    telegram_bot_api_key = sys.argv[3]

    since = readSince()
    
    print(f"Since read: {since}\n")

    bot = telegram.Bot(token=telegram_bot_api_key)

    allArticles = loadArticles(since, False)
    print(f'All articles:\n {json.dumps(allArticles).encode("utf-8")}\n')
    
    data = loadArticles(since, True)
    print(f'Articles to post:\n {json.dumps(data).encode("utf-8")}\n')

    if 'list' in data and len(data["list"]) > 0:
        items = mapArticles(data)
        
        for item in items:
            try:
                bot.send_message(chat_id="@krossovochkin_newsletter", text=item[0], parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)
                
                message = item[0].encode("utf-8")
                print(f"Message sent: \n{message}\n")

                since = item[1]
                saveSince(since)
                
                print(f"Since saved: {since}")
            except Exception as e:
                print(f"Error: {e}")
