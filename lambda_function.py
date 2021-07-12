import json
import boto3
import base64
from datetime import date
from botocore.exceptions import ClientError

from GordonGrowth import GordonGrowthModel
from IEXCloud import IEXCloudAPI

from db import ticker_confirm, store_gordon_growth, get_tick_date

def lambda_handler(event, context):

    try:
        
        secrets_client = boto3.client('secretsmanager')
        secret_arn = 'arn:aws:secretsmanager:us-east-1:133800649937:secret:IEX_API_KEY-cOd2vB'
        IEX_CLOUD_API_KEY_RYAN = secrets_client.get_secret_value(SecretId=secret_arn).get('SecretString')
        IEX_CLOUD_API_KEY_RYAN = json.loads(IEX_CLOUD_API_KEY_RYAN)['IEX_CLOUD_API_KEY_RYAN']
        
        symbol = event['queryStringParameters']['symbol']
        
        cached = False
        
        if ticker_confirm(symbol):
            cached = True
            Resp = get_tick_date(symbol)
            response_date = Resp['date_created']
            response_date = int(response_date.replace('-',''))
            
            if response_date - int(str(date.today()).replace('-','')) < 7:
                results = get_tick_date(symbol)
                results['cached'] = cached
                return {
                    'statusCode': 200,
                    'body': json.dumps(results, indent=4)
                }
        else:
            model = GordonGrowthModel()
            api = IEXCloudAPI(IEX_CLOUD_API_KEY_RYAN)
            
            dividend_content = api.dividend_info(symbol)
            split_content = api.split_info(symbol)
            stats_content = api.stats_info(symbol)
            
            dividend_amount = dividend_content[0]['amount']
            dgr = model.dividend_growth_rate(symbol, dividend_content, split_content) 
            
            edps = model.expected_dividends_per_share(dgr, dividend_amount)
            
            rm = 0.1125
            rf = 0.0221
            
            #Assuming quartly dividends
            next_div_date = 3
            days_till_next_div = 0
            
            if stats_content['nextDividendDate']:
            	days_till_next_div = datetime.strptime(stats_content['nextDividendDate'], '%Y-%m-%d') - date.today()
            
            beta = stats_content['beta']
            coe = model.cost_of_capital_equity(beta, rf, rm)
            
            # quarterly dividends only 
            ggm_value = model.value(edps, coe, dgr)
            
            try:
                store_gordon_growth(symbol, dgr, edps, coe, ggm_value)
            except:
                pass
            
            results = {
                "cached": cached,
            	"symbol": symbol,
            	"dividend_growth_rate": dgr,
            	"expected_dividends_per_share": edps,
            	"cost_of_equity": coe,
            	"gordon_growth_value": ggm_value
            }

            return {
                'statusCode': 200,
                'body': json.dumps(results, indent=4)
            }
    
    except IndexError as e:
        return {
            'statusCode': 200,
            'body': json.dumps('No dividend information available.')
        }
    except ZeroDivisionError as e:
        return {
            'statusCode': 200,
            'body': json.dumps('Insufficient information available.')
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps(str(e))
        }
