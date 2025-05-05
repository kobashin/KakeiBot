import requests
import os
import time
from datetime import datetime, timedelta
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

# This function will be invoked by AWS EventBridge/Lambda.
# Schedule expression is "cron(0 23 ? * SUN *)".
# Start time is 00:00 JST on last Monday.
# End time is 23:59 JST on last Sunday.
# The time zone is Asia/Tokyo (JST).
# For example, if this function is invoked 23:00 on 2025-05-04 (Sunday),
# the start_time is 00:00 on 2025-04-28 (Monday) and the end_time is 23:59 on 2025-05-04 (Sunday).

now = datetime.now(ZoneInfo('Asia/Tokyo'))
# To get start_time, we need to subtract 6 days from the current date and set the time to 00:00.
start_time = now - timedelta(days=6)
start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
# To get end_time, we need to set the time to 23:59.
end_time = now.replace(hour=23, minute=59, second=0, microsecond=0)

# To get the date in the format YYYY-MMDD-HHMM, we need to format the date.
start_time_str = start_time.strftime('%Y-%m%d-%H%M')
end_time_str = end_time.strftime('%Y-%m%d-%H%M')
start_time_str_short = start_time.strftime('%m%d')
end_time_str_short = end_time.strftime('%m%d')


def get_food():
    response = dynamodb.scan(
        TableName='KakeiBot-Table',
        FilterExpression=(
            '(category = :food) '
            'AND (#dt BETWEEN :start AND :end)'
        ),
        ExpressionAttributeNames={
            '#dt': 'date'
        },
        ExpressionAttributeValues={
            ':food': {'S': '食費'},
            ':start': {'S': start_time_str},
            ':end': {'S': end_time_str}
        }
    )
    summary = {
        '自炊': 0,
        '外食': 0,
        'その他': 0
    }
    for item in response['Items']:
        sub_category = item['sub-category']['S']
        price = int(item['price']['S'])
        if sub_category not in summary:
            summary['その他'] += price
        else:
            summary[sub_category] += price

    tmp_food = [f"{key}:{value}円" for key, value in summary.items()]
    tmp_food = '\n'.join(tmp_food)
    food = f"[食費]\n{tmp_food}"
    return food


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
            ':start': {'S': start_time_str},
            ':end': {'S': end_time_str}
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
    tmp_deposit = [f"{key}:{value}円" for key, value in summary.items()]
    tmp_deposit = '\n'.join(tmp_deposit)
    deposit = f"[拠出金額]\n{tmp_deposit}"
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
    message = "先週({}~{})の出費\n{}\n{}".format(
        start_time_str_short,
        end_time_str_short,
        get_food(),
        get_deposit()
    )

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
