import json
import os
from botocore.vendored import requests
import time
from calendar import timegm
import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime, date, time, timezone, timedelta
from decimal import Decimal
import decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('new-app-DynamoDBTable-Z80C5KUBSYR8')


#For serialization of json decimal data into string
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return {'__Decimal__': str(obj)}
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

def as_Decimal(dct):
    if '__Decimal__' in dct:
        return decimal.Decimal(dct['__Decimal__'])
    return dct

def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    requested_symbol = event['queryStringParameters']['symbol']

    timenowFloat = datetime.now().timestamp()
    timenowInt = int(timenowFloat)

    dt = datetime.now() - timedelta(7)
    eTimeSevenDaysBack = int(dt.timestamp())

    response = table.query(
        KeyConditionExpression=Key('symbol').eq(requested_symbol) & Key('eTime').gt(eTimeSevenDaysBack)
    )

    items = response['Items']
    print(items)

    max = 0
    min = 1000000

    for item in items:
        highVal = float(item.get('high_Price'))
        lowVal = float(item.get('low_Price'))

        if(highVal > max):
            max=highVal
        elif(lowVal < min):
            min=lowVal

    stats = { 'Maximum of '+ str(requested_symbol) : max, 'Minimum of '+str(requested_symbol): min}



    return {
        "statusCode": 200,
        "body": json.dumps(stats, cls=DecimalEncoder),
    }
