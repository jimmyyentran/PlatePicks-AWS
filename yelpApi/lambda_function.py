from __future__ import print_function

import json
from yelpApi import Yelp_API
from dynamodb import DB

class DatabaseError(Exception):
    pass

print('Loading function')

def lambda_handler(event, context):
    try:
        response = Yelp_API(event).call_API()
    except RuntimeError as re:
        raise DatabaseError(re.message)

    print(response)

    if not response:
        raise DatabaseError("NoFoodException")

    return response # Echo back the first key value

def lambda_handler_insertToDB(event, context):
    print(event)
    DB().fill_empty_restaurant(json.loads(event['Records'][0]['Sns']['Message']))
