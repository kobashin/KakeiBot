import json
import logging
import os
import sys

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# INFOレベル以上のログメッセージを拾うように設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 環境変数からチャネルアクセストークンキー取得
CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')
# 環境変数からチャネルシークレットキーを取得
CHANNEL_SECRET = os.getenv('CHANNEL_SECRET')

# それぞれ環境変数に登録されていないとエラー
if CHANNEL_ACCESS_TOKEN is None:
    logger.error(
        'LINE_CHANNEL_ACCESS_TOKEN is not defined as environmental variables.')
    sys.exit(1)
if CHANNEL_SECRET is None:
    logger.error(
        'LINE_CHANNEL_SECRET is not defined as environmental variables.')
    sys.exit(1)

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
webhook_handler = WebhookHandler(CHANNEL_SECRET)

# ユーザーからのメッセージを処理する
@webhook_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    answer = event.message.text
    # 応答トークンを使って回答を応答メッセージで送る
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text=answer))

def lambda_handler(event, context):

    # ヘッダーにx-line-signatureがあることを確認
    if 'x-line-signature' in event['headers']:
        signature = event['headers']['x-line-signature']

    body = event['body']
    # 受け取ったWebhookのJSON
    logger.info(body)

    try:
        webhook_handler.handle(body, signature)
    except InvalidSignatureError:
        # 署名を検証した結果がLINEプラットフォームからのWebhookでなければ400を返す
        return {
            'statusCode': 400,
            'body': json.dumps('Webhooks are accepted exclusively from the LINE Platform.')
        }
    except LineBotApiError as e:
        # 応答メッセージを送る際LINEプラットフォームからエラーが返ってきた場合
        logger.error('Got exception from LINE Messaging API: %s\n' % e.message)
        for m in e.error.details:
            logger.error('  %s: %s' % (m.property, m.message))

    return {
        'statusCode': 200,
        'body': json.dumps('Success!')
    }
