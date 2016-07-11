from __future__ import print_function  # Python 2/3 compatibility

import json

import boto3
import decimal
from decimal import Decimal
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from multiprocessing.pool import ThreadPool
from threading import Thread
from crawl import Crawler
from random import shuffle


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


class DB(object):
    def __init__(self, data):
        # Global so these can be used anywhere
        global table
        food_db = boto3.Session(
            aws_access_key_id='AKIAJLUAEUTHWQCBK5RQ',
            aws_secret_access_key='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'
        )

        # Hardcoded in key parameters
        dynamodb = food_db.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('foodtinder-mobilehub-761050320-food')
        self.restaurant_table = dynamodb.Table('foodtinder-mobilehub-761050320-restaurant')

        self.urls = data;
        self.information = []
        self.empty_restaurant = {}

    def query(self, limit=1):
        self.limit = limit
        list_of_locations = []
        #  p = ThreadPool(20) #ThreadPool requires number input
        p = ThreadPool()  # ThreadPool requires number input
        # for key in self.urls:
        #     list_of_locations.append(self.urls[key])

        # result = p.map_async(get_food_from_restaurant, list_of_locations, callback=self.mycallback)
        # Do shuffling
        # shuffle(list_of_locations)
        # try:
        #     p.map(self.get_food_from_restaurant, list_of_locations);
        #     # map(self.get_food_from_restaurant, list_of_locations);
        # except Exception as e:
        #     print(e)

        for key, value in self.urls.iteritems():
            p.apply_async(self.get_food_from_restaurant, [value])

        p.close()
        p.join()

        thread = Thread(target=self.fill_empty_restaurant, args=[self.empty_restaurant])
        thread.start()

        return self.information

    def fill_empty_restaurant(self, item):
        # It there is an empty restaurant, then add
        if self.empty_restaurant:
            print("Attempting to add empty restaurants to DB")
            p = ThreadPool()

            try:
                for key, value in self.empty_restaurant.iteritems():
                    p.apply_async(self.upload_restaurant_item, [value])
            except Exception as e:
                # Sometimes this will throw, but it will execute anyways
                print(e)

            p.close()
            p.join()

            # self.upload_restaurant_list(self.empty_restaurant)

            print("Attempting to add food through YelpApi")
            self.upload_food_list(Crawler(self.empty_restaurant).query(10))


        return

    def mycallback(self, x):
        # Add only non-empty lists
        #  for restaurant in x:
        #  if restaurant:
        #  self.information.extend(restaurant)
        print(x)

    def check_if_restaurant_exists(self, restaurantId):
        # Send request
        response = self.restaurant_table.query(
            KeyConditionExpression=Key('restaurantId').eq(restaurantId)
        )

        if response['Count'] >= 1:
            print("Exists: " + restaurantId)
            return True
        else:
            print("Doesn't Exist: " + restaurantId)
            return False

    def get_food_from_restaurant(self, location):
        restaurantId = location['restaurantId']
        try:
            response = table.query(
                ProjectionExpression="#name, foodId",
                ExpressionAttributeNames={"#name": "name"},
                IndexName='restaurantId-index',
                KeyConditionExpression=Key('restaurantId').eq(restaurantId),
                Limit=self.limit
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            food_list = []
            items = response['Items']
            for item in items:
                url = "http://s3-media3.fl.yelpcdn.com/bphoto/" + item["foodId"] + "/o.jpg"
                single_food_item = dict(url=url, food_id=item["foodId"],
                                        name=item["name"], location=location)
                food_list.append(single_food_item)

            if food_list:
                self.information.extend(food_list)
            else:
                # if empty list, print the restaurantId
                print("No food from: " + restaurantId)

                # Do a check to see if the restaurant exists, if it does we know that the restaurant doesn't have
                # any pictures, so continue
                if not self.check_if_restaurant_exists(restaurantId):
                    self.empty_restaurant[restaurantId] = location

            return food_list

    # Upload single item
    def upload_food_item(self, item):
        foodId = item["food_id"]
        restaurantId = item['location']['restaurantId']
        name = item['name']

        try:
            response = table.put_item(
                Item={
                    'foodId': foodId,
                    'restaurantId': restaurantId,
                    'name': name
                },
                ConditionExpression='attribute_not_exists(foodId)'
            )
            print("Success: {} {}".format(foodId, restaurantId))
            json.dumps(response, indent=4, cls=DecimalEncoder)
        except Exception as e:
            print(e)
            print("Food Insert Fail: {}".format(foodId))

    # Upload from yelpApi list (cap 20)
    def upload_food_list(self, data):
        for item in data:
            self.upload_food_item(item)

    # Upload single item
    def upload_restaurant_item(self, item):

        # Convert float -> string -> decimal
        restaurantId = item['restaurantId']
        restaurant_name = item['restaurant_name']
        address = item['address']
        categories = item['category']
        city = item['city']
        latitude = Decimal(str(item['latitude']))
        longitude = Decimal(str(item['longitude']))
        postal_code = int(item['postal_code'])
        state = item['state']
        try:
            response = self.restaurant_table.put_item(
                Item={
                    'restaurantId': restaurantId,
                    'address': address,
                    'categories': categories,
                    'city': city,
                    'latitude': latitude,
                    'longitude': longitude,
                    'postal_code': postal_code,
                    'restaurant_name': restaurant_name,
                    'state': state
                },
                ConditionExpression='attribute_not_exists(restaurantId)'
            )
            print(u"Add restaurant Success: {}".format(restaurantId))
            #  json.dumps(response, indent=4, cls=DecimalEncoder)
        except ClientError as ce:
            if ce.response['Error']['Code'] == "ConditionalCheckFailedException":
                print(u"Fail (already exists): {}".format(restaurantId))
        except Exception as e:
            print(u"Add restaurant Fail: {}".format(restaurantId))
            print(e)

    # Upload from yelpApi list (cap 20)
    def upload_restaurant_list(self, data):
        for key, value in data.iteritems():
            self.upload_restaurant_item(value)

if __name__ == "__main__":
    DB().get_item()
