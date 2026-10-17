import json
import time
import boto3
from datetime import datetime
from zoneinfo import ZoneInfo

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('KakeiBot-Table')

cors_headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
}


def convert_ui_date_to_dynamo_format(date_str):
    """YYYY-MM-DD → YYYY-MMDD-1200（HHMM部分は1200固定）"""
    if date_str:
        parts = date_str.split('-')  # ['2026', '10', '12']
        year = parts[0]
        month_day = parts[1] + parts[2]  # '1012'
        return f"{year}-{month_day}-1200"
    else:
        now = datetime.now(ZoneInfo('Asia/Tokyo'))
        return now.strftime('%Y-%m%d') + '-1200'


def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}")

    method = event.get('httpMethod', 'POST')

    if method == 'OPTIONS':
        return {'statusCode': 200, 'headers': cors_headers, 'body': ''}

    if method != 'POST':
        return {
            'statusCode': 405,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Method not allowed'})
        }

    try:
        body = json.loads(event.get('body', '{}'))

        category = body.get('category')
        price = body.get('price')
        if not category or price is None:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'category and price are required'})
            }

        item = {
            'userID': 'web-ui',
            'timestamp': int(time.time() * 1000),
            'groupID': '-',
            'date': convert_ui_date_to_dynamo_format(body.get('date')),
            'category': category,
            'sub-category': body.get('subCategory', '-'),
            'price': int(price),
            'memo': body.get('memo') or '-',
        }

        table.put_item(Item=item)
        print(f"Item registered: {item}")

        return {
            'statusCode': 201,
            'headers': cors_headers,
            'body': json.dumps(
                {'message': 'Item registered', 'item': item},
                ensure_ascii=False, default=str
            )
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'error': str(e)})
        }
