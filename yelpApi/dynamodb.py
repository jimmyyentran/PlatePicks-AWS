from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import decimal
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from multiprocessing import Pool

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

def get_food_from_restaurant(location):
    #  dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    #  table = dynamodb.Table('foodtinder-mobilehub-761050320-food')
    #  table = dynamodb.Table('foodtinder-mobilehub-761050320-food')
    restaurantId = location['restaurantId']
    try:
        response = table.query(
                ProjectionExpression="#name, foodId",
                ExpressionAttributeNames={ "#name": "name" },
                IndexName='restaurantId-index',
                KeyConditionExpression=Key('restaurantId').eq(restaurantId)
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        #  print(response)
        food_list = []
        items = response['Items']
        for item in items:
            url = "http://s3-media3.fl.yelpcdn.com/bphoto/" + item["foodId"] + "/o.jpg"
            single_food_item = dict(url=url, food_id=item["foodId"],
                    name=item["name"], location=location)
            food_list.append(single_food_item)
        #  print("GetItem succeeded:")
        #  print("Done: " + restaurantId )
        #  print(json.dumps(item, indent=4, cls=DecimalEncoder))
        #  print(food_list)
        if not food_list:
            print(restaurantId)

        return food_list

class DB(object):
    def __init__(self, data):
        #Global so these can be used anywhere
        global table
        food_db = boto3.Session(
                aws_access_key_id ='AKIAJLUAEUTHWQCBK5RQ',
                aws_secret_access_key='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'
        )
        #  dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        #  table = dynamodb.Table('foodtinder-mobilehub-761050320-food')
        dynamodb = food_db.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('foodtinder-mobilehub-761050320-food')

        self.urls = data;
        self.information = []


    def query(self, limit):
        list_of_locations = []
        p = Pool()
        for key in self.urls:
            list_of_locations.append(self.urls[key])

        result = p.map_async(get_food_from_restaurant, list_of_locations, callback=self.mycallback)
        result.wait()
        return self.information

    def mycallback(self, x):
        # Add only non-empty lists
        for restaurant in x:
            if restaurant:
                self.information.extend(restaurant)

if __name__ == "__main__":
    DB().get_item()
