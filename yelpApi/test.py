from yelpApi import Yelp_API
import pprint
import time

#Test Parameters
params = {
        "term": "asian",
       "food_per_business": 1,
       "ll": "33.9533, -117.3962",
       "limit": 20,
       "radius_filter": 40000,
       "category_filter": "vietnamese,filipino",
       "sort": 1,
       "offset": 0,
       "query_method": 1
        }

params2 = {
        "term": "asian",
       "food_per_business": 1,
       "ll": "33.9533, -117.3962",
       "limit": 20,
       "radius_filter": 40000,
       "category_filter": "vietnamese,filipino",
       "sort": 1,
       "offset": 0,
       "query_method": 0
        }

start = time.time()
response = Yelp_API(params).call_API()
end = time.time()
pprint.pprint(response)

start2 = time.time()
response = Yelp_API(params2).call_API()
end2 = time.time()
pprint.pprint(response)

print("Query database:")
print (end - start)
print("Yelp on-the-fly: ")
print(end2 - start2)
