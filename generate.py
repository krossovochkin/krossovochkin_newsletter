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

bot = telegram.Bot(token=telegram_bot_api_key)

response = requests.get(f'https://getpocket.com/v3/get?consumer_key={consumer_key}&access_token={access_token}&state=archive&detailType=complete&since={since}&sort=newest&tag=newsletter').content

data = json.loads(response)

def mapItem(item):
	title = item['resolved_title']
	url = item['resolved_url']
	description = item['excerpt']
	authors = ",".join(list(map(lambda kv: kv[1]['name'], item.get("authors", {}).items())))
	return f"✍️ {authors}\n🏷️ [{title}]({url})\n📜 {description}"

items = list(map(lambda kv: kv[1], data["list"].items()))

if len(items) != 0:
	newsletter = "\n\n".join(list(map(lambda x: mapItem(x), items)))
	bot.send_message(chat_id="@krossovochkin_newsletter", text=newsletter, parse_mode=telegram.ParseMode.MARKDOWN)
