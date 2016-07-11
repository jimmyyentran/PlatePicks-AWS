from yelpApi import Yelp_API
import pprint
import time

#Test Parameters
params =  {
        #  "term": "",
       #  "food_per_business": 1,
       #  "ll": "33.9513, -118.3940",
       #  "limit": 20,
       #  "radius_filter": 40000,
       #  "category_filter": "",
       #  "sort": 1,
       #  "offset": 0,
       #  "query_method": 1
        #  }

  "term": "",
  "food_per_business": 1,
  "ll": "40.3033, -75.2945",
  "limit": 20,
  "radius_filter": 10000,
  "category_filter": "",
  "sort": 1,
  "query_method": 1
}
response = Yelp_API(params).call_API()
pprint.pprint(response)
