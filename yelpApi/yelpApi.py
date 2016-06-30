import io
import json
from pprint import pprint
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator
from yelp.config import SEARCH_PATH
from yelp.obj.search_response import SearchResponse
from crawl import Crawler
from dynamodb import DB
import datetime

# This class serves as Yelp API's wrapper
# param: python dictionary with
class Yelp_API(object):
    def __init__(self, data):
        #authorization
        with io.open('config_secret2.json') as cred:
            creds = json.load(cred)
            auth = Oauth1Authenticator(**creds)
            self.client = Client(auth)
            self.data = data

        # own parameters being passed in
        self.food_per_business = data['food_per_business']

    def call_API(self):
        response = SearchResponse(
                self.client._make_request(SEARCH_PATH, self.data)
                )

        list_to_be_returned = []
        dict_of_urls = {}
        for bus in response.businesses:
            url = "http://www.yelp.com/biz_photos/"+bus.id+"?tab=food&start=0"
            category_list = []
            for category in bus.categories:
                category_list.append(category.name)

            dict_of_urls[url]= dict(address=bus.location.address, 
                    city=bus.location.city,
                    state=bus.location.state_code,
                    postal_code=bus.location.postal_code,
                    display_address=bus.location.display_address,
                    restaurant_name=bus.name,
                    restaurantId = bus.id,
                    latitude=bus.location.coordinate.latitude,
                    longitude=bus.location.coordinate.longitude,
                    category=category_list
                    )

        if 'query_method' in self.data and self.data['query_method'] == 1:
            print("DB")
            return DB(dict_of_urls).query(self.food_per_business)
        else:
            print("Yelp")
            return Crawler(dict_of_urls).query(self.food_per_business)
