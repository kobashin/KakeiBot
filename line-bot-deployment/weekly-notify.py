import requests
import os
import boto3

# DynamoDBに接続し、テーブル 'KakeiBot-Table' を指定
dynamodb = boto3.resource('dynamodb')
# table = dynamodb.Table('KakeiBot-Table')
description = dynamodb.describe_table(TableName='KakeiBot-Table')
table_size_bytes = description['Table']['TableSizeBytes']


def lambda_handler(event, context):
    # 3. Lambdaの環境変数からLINEのアクセストークンとユーザーIDを取得
    line_token = os.environ['CHANNEL_ACCESS_TOKEN']
    group_id = os.environ['GROUP_ID']  # 送信先ユーザーID

    # ここで送信するメッセージ内容を作成（後でDynamoDBから取得したサマリーに置き換える）
    message = "Test : weekly-notify.py\n" + \
        "DynamoDBのテーブル名はKakeiBot-Tableです。\n" + \
        "DynamoDBのテーブルサイズは" + str(table_size_bytes) + "バイトです。"

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
