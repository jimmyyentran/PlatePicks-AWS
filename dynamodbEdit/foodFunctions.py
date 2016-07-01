from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import decimal
import string
from boto3.dynamodb.conditions import Key, Attr

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

class DynamodbEdit(object):
    def __init__(self):
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        self.table = dynamodb.Table('foodtinder-mobilehub-761050320-food')

    def scan_for_apostrophe(self):
        ae = Attr('name').contains("'")
        pe = "#name, foodId"
        ean = { "#name":"name" }

        response = self.table.scan(
                FilterExpression=ae,
                ProjectionExpression=pe,
                ExpressionAttributeNames=ean
                )

        for i in response['Items']:
            print(json.dumps(i, cls=DecimalEncoder))


    def lowercase_after_apostrophe(self):
        ae = Attr('name').contains("'")
        pe = "#name, foodId"
        ean = { "#name":"name" }

        response = self.table.scan(
                FilterExpression=ae,
                ProjectionExpression=pe,
                ExpressionAttributeNames=ean
                )

        for i in response['Items']:
            #  print(json.dumps(i, cls=DecimalEncoder))
            newName = self.remove_capitalization_after_apostrophe(i["name"])
            self.update_new_food_name(i["foodId"], newName)

    def update_new_food_name(self, foodId, foodName):
        response = self.table.update_item(
                Key={"foodId": foodId},
                UpdateExpression="set #name = :n",
                ExpressionAttributeValues={
                    ':n': foodName
                },
                ExpressionAttributeNames={
                    "#name": "name"
                }
        )

        print("Success!")
        #  print("{}: {}".format(foodId, foodName))
        #  print(json.dumps(response, indent=4, cls=DecimalEncoder))

    def remove_capitalization_after_apostrophe(self, str):
        return string.capwords(str)


if __name__ == "__main__":
    #  DynamodbEdit().scan_for_apostrophe()
    #  DynamodbEdit().lowercase_after_apostrophe()
    #  DynamodbEdit().update_new_food_name('testIdx', 'newName')
    DynamodbEdit().scan_for_apostrophe()

