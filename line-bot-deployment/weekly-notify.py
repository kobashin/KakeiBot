import requests
import os
import time
import boto3

# DynamoDBに接続し、テーブル 'KakeiBot-Table' を指定
dynamodb = boto3.resource('dynamodb')
# table = dynamodb.Table('KakeiBot-Table')

# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/describe_table.html
# wait for 3 seconds not to get "ResouurceNotFoundException"
# the reason is noted in the URL above
time.sleep(3)
description = dynamodb.describe_table(TableName='KakeiBot-Table')
table_size_bytes = description['Table']['TableSizeBytes']
table_item_count = description['Table']['ItemCount']


def lambda_handler(event, context):
    # 3. Lambdaの環境変数からLINEのアクセストークンとユーザーIDを取得
    line_token = os.environ['CHANNEL_ACCESS_TOKEN']
    group_id = os.environ['GROUP_ID']  # 送信先ユーザーID

    # ここで送信するメッセージ内容を作成（後でDynamoDBから取得したサマリーに置き換える）
    message = "Test : weekly-notify.py\n" + \
        "DynamoDBのテーブル名はKakeiBot-Tableです。\n" + \
        "KakeiBot-Tableのアイテム数は" + str(table_item_count) + "件です。\n" + \
        "KakeiBot-Tableのサイズは" + str(table_size_bytes) + "バイトです。"

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
