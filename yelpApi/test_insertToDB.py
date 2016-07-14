from dynamodb import DB
import json
from crawl import Crawler
import threading

#Test Parameters
with open('params.json', 'r') as file:
    json_sns=file.read()


# DB().fill_empty_restaurant(json.loads(json_sns))
t = threading.Thread(name="Crawler", target=DB().upload_food_list(Crawler(json.loads(json_sns)).query(10)))
t.start()
t.join()
print("NEXT")

