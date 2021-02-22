import requests
import urllib
import sys
import json
import telegram
from datetime import datetime, timedelta
import time
import os.path

consumer_key = sys.argv[1]
access_token = sys.argv[2]
telegram_bot_api_key = sys.argv[3]

since = int(time.mktime((datetime.now() - timedelta(1)).timetuple()))

file_name = "temp"
if os.path.exists(file_name):
    with open(file_name, "r") as f:
        since = int(f.readline())

bot = telegram.Bot(token=telegram_bot_api_key)

response = requests.get(f'https://getpocket.com/v3/get?consumer_key={consumer_key}&access_token={access_token}&state=archive&detailType=complete&since={since}&sort=oldest&tag=newsletter').content

data = json.loads(response)

def mapItem(item):
    title = item['resolved_title']
    url = item['resolved_url']
    description = item['excerpt']
    authors = ",".join(list(map(lambda kv: kv[1]['name'], item.get("authors", {}).items())))
    if authors:
        return f"✍️ {authors}\n🏷️ [{title}]({url})\n📜 {description}"
    else:
        return f"🏷️ [{title}]({url})\n📜 {description}"

if 'list' in data and len(data["list"]) > 0:
    with open(file_name, "w") as f:
        f.write(str(int(time.mktime(datetime.now().timetuple()))))

    items = list(map(lambda kv: kv[1], data["list"].items()))
    items = list(filter(lambda x: int(x['time_read']) >= since, items))
    items = list(map(lambda x: mapItem(x), items))
    
    for item in items:
        bot.send_message(chat_id="@krossovochkin_newsletter", text=item, parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)
