import os
import boto3 
from boto3.dynamodb.conditions import Key
import json
from datetime import date, timedelta, datetime
from botocore.exceptions import ClientError 
from decimal import Decimal


region_name = 'us-east-1'

dynamo = boto3.resource('dynamodb', region_name = region_name, aws_access_key_id= aws_access_key_id, aws_secret_access_key = aws_secret_access_key, aws_session_token= aws_session_token)


def ticker_confirm(symbol):
	try:
		table = dynamo.Table('ticker')
		scan_kwargs = {
			'FilterExpression': Key('symbol').eq(symbol)
		}
		result = table.scan(**scan_kwargs)['Items'][0]
	except:
		return False
	return True 


def store_gordon_growth(symbol,dgr,edps,coe,ggm_value):
	table = dynamo.Table('ticker')
	response = table.update_item(
		Key={
			'symbol': symbol,
		},
		UpdateExpression="SET dgr= :r, expected_dividends_per_share= :e, cost_of_equitys= :c, gordon_growth_value= :g, date_created= :d",
		ExpressionAttributeValues={
			':r': Decimal(str(dgr)),
			':e': Decimal(str(edps)),
			':c': Decimal(str(coe)),
			':g': Decimal(str(ggm_value)),
			':d': str(date.today())
		},
	)

	return response


def get_tick_date(symbol):
	try:
		table = dynamo.Table('ticker')
		response = table.get_item(Key={'symbol':symbol})
	except ClientError as e:
		#print(e.response['Error']['Message'])
		pass
	else:
		result = response['Item']
		
		for key in result:
			if type(result[key]) == type(Decimal()):
					result[key] = float(result[key])
			
		return result
