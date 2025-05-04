import requests
import os
import time
from datetime import datetime
from zoneinfo import ZoneInfo
import boto3

# DynamoDBに接続し、テーブル 'KakeiBot-Table' を指定
dynamodb = boto3.client('dynamodb')
# table = dynamodb.Table('KakeiBot-Table')

# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/describe_table.html
# wait for 3 seconds not to get "ResouurceNotFoundException"
# the reason is noted in the URL above
time.sleep(3)
# description = dynamodb.describe_table(TableName='KakeiBot-Table')
# table_size_bytes = description['Table']['TableSizeBytes']
# table_item_count = description['Table']['ItemCount']

# This function will be invoked by AWS Lambda.
# Schedule expression is "cron(0 8 ? * MON *)".

def get_deposit():
    response = dynamodb.scan(
        TableName='KakeiBot-Table',
        FilterExpression=(
            '(category = :deposit OR category = :withdrawal) '
            'AND (#dt BETWEEN :start AND :end)'
        ),
        ExpressionAttributeNames={
            # 'date' is a reserved word, so use ExpressionAttributeNames
            '#dt': 'date'
        },
        ExpressionAttributeValues={
            ':deposit': {'S': '入金'},
            ':withdrawal': {'S': '拠出'},
            ':start': {'S': '2025-0428-0000'},
            ':end': {'S': '2025-0504-2359'}
        }
    )

    # sum up prices for each sub-category
    """
        Each item is like that.
            {
                'sub-category': {'S': '真一郎'}, 
                'date': {'S': '2025-0501-1842'}, 
                'userID': {'S': 'U55f2c6b5b...'}, 
                'timestamp': {'N': '1746092545035'}, 
                'category': {'S': '入金'}, 
                'memo': {'S': '-'}, 
                'price': {'S': '10000'}
            }
    """

    summary = {}
    # iterate over items
    for item in response['Items']:
        sub_category = item['sub-category']['S']
        price = int(item['price']['S'])
        # if sub-category is not in summary, add it
        if sub_category not in summary:
            summary[sub_category] = 0
        # add price to sub-category
        summary[sub_category] += price

    # print summary
    tmp_deposit = [f"{key}:{value}" for key, value in summary.items()]
    tmp_deposit = '\n'.join(tmp_deposit)
    deposit = f"Deposit of last week\n{tmp_deposit}"
    return deposit


def lambda_handler(event, context):
    # 3. Lambdaの環境変数からLINEのアクセストークンとユーザーIDを取得
    line_token = os.environ['CHANNEL_ACCESS_TOKEN']
    group_id = os.environ['GROUP_ID']  # 送信先ユーザーID

    # ここで送信するメッセージ内容を作成（後でDynamoDBから取得したサマリーに置き換える）
    """
    message = "Test : weekly-notify.py\n" + \
        "DynamoDBのテーブル名はKakeiBot-Tableです。\n" + \
        "KakeiBot-Tableのアイテム数は" + str(table_item_count) + "件です。\n" + \
        "KakeiBot-Tableのサイズは" + str(table_size_bytes) + "バイトです。"
    """
    message = get_deposit()

    # LINE Messaging API用のヘッダーを設定
    headers = {
        "Authorization": f"Bearer {line_token}",
        "Content-Type": "application/json"
    }
    # 送信するデータ（宛先ユーザーIDとメッセージ内容）を設定
    data = {
        "to": group_id,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    # 4. Lambdaでrequestsパッケージを使ってLINE Messaging APIにPOSTリクエストを送信
    response = requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers=headers,
        json=data
    )
    # レスポンスを返す（Lambdaの実行結果として）
    return {
        'statusCode': response.status_code,
        'body': response.text
    }
