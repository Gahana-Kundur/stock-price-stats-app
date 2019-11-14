import json
import os
from botocore.vendored import requests
import time
from calendar import timegm
import boto3

# import requests

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('new-app-DynamoDBTable-Z80C5KUBSYR8')

def get_stock_quote(symbol):
    api_key =  os.environ['API_KEY']
    response = requests.get(f'https://www.alphavantage.co/query?apikey={api_key}&function=GLOBAL_QUOTE&symbol={symbol}')
    return response.json()['Global Quote']

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

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e
    print("Before calling")
    stocks = ["FB", "AAPL", "AMZN", "NFLX", "GOOG"]
    for stock in stocks:

        info_price = get_stock_quote(stock)
        #deserialisedDtata = json.loads(info_price)
        symbol = info_price['01. symbol']
        lowPrice = info_price['04. low']
        highPrice = info_price['03. high']
        tradingDate = info_price['07. latest trading day']
        priceAtTheEnd = info_price['05. price']
        utc_time = time.strptime(tradingDate, "%Y-%m-%d")
        epoch_time = timegm(utc_time)
        print("Converted epoch time for {} is {}".format(tradingDate, epoch_time))
        print(symbol, lowPrice, highPrice,epoch_time,priceAtTheEnd)

        table.put_item(
       Item={
            'symbol': symbol,
            'low_Price': lowPrice ,
            'high_Price': highPrice,
            'eTime': epoch_time,
            'finalPrice': priceAtTheEnd,

        }
       )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": " Hello from GKJ"
            # "location": ip.text.replace("\n", "")
        }),
    }
