from yelpApi import Yelp_API
import pprint
import time

#Test Parameters
params = {
        "term": "",
       "food_per_business": 1,
       "ll": "33.9513, -116.9940",
       "limit": 20,
       "radius_filter": 40000,
       "category_filter": "",
       "sort": 1,
       "offset": 0,
       "query_method": 1
        }
response = Yelp_API(params).call_API()
pprint.pprint(response)
