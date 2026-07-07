import json
import logging
import os
import sys
import boto3
from funcs import (
    make_table_item_from_text,
    make_table_item_from_image,
    makeResponseMessage,
    resize_image,
    generate_s3_key,
    upload_image_to_s3,
    generate_s3_key_for_json,
    upload_json_to_s3
)

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    ImageMessage
)
from io import BytesIO


# DynamoDBに接続し、テーブル 'household_account' を指定
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('KakeiBot-Table')

# S3クライアント初期化
s3_client = boto3.client('s3')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'kakeibot-receipt')

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

    # get message text
    tmp_text = event.message.text
    # make a table item put into DynamoDB
    item = make_table_item_from_text(tmp_text, event)
    # make a response for LINE bot
    response = makeResponseMessage(item)

    # put item into DynamoDB
    table.put_item(Item=item)

    # 応答トークンを使って回答を応答メッセージで送る
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text=response))


# 画像メッセージを処理する
@webhook_handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    try:
        # 画像メッセージのIDを取得
        message_id = event.message.id

        # LINE APIから画像コンテンツを取得
        message_content = line_bot_api.get_message_content(message_id)

        # 画像データを読み込む
        image_data = BytesIO()
        for chunk in message_content.iter_content():
            image_data.write(chunk)
        image_data.seek(0)

        # 画像サイズをチェックし、必要に応じてリサイズ
        image_bytes = image_data.getvalue()
        image_size_mb = len(image_bytes) / (1024 * 1024)

        logger.info(f"Original image size: {image_size_mb:.2f}MB")

        # 4MB以上の場合はリサイズ
        if image_size_mb >= 4:
            logger.info("Resizing image...")
            resized_bytes = resize_image(image_bytes)
            image_data_for_processing = BytesIO(resized_bytes)
        else:
            image_data_for_processing = BytesIO(image_bytes)

        # S3に画像を保存（失敗しても処理継続）
        try:
            # S3キーを生成
            s3_key = generate_s3_key(
                event.source.user_id,
                event.timestamp,
                message_id
            )
            logger.info(f"Uploading image to S3: {s3_key}")

            # S3にアップロード
            upload_image_to_s3(
                image_data_for_processing.getvalue(),
                s3_key,
                S3_BUCKET_NAME,
                s3_client
            )
            logger.info(f"S3 upload successful: {s3_key}")

            # S3情報を保存用に記録
            s3_info = {
                's3_image_key': s3_key,
                's3_bucket': S3_BUCKET_NAME,
                's3_upload_status': 'success'
            }
        except Exception as s3_error:
            logger.error(f"S3 upload failed: {str(s3_error)}")
            # S3保存失敗時も処理継続
            s3_info = {
                's3_upload_status': 'failed',
                's3_error_message': str(s3_error)[:200]
            }

        # Azure解析用のデータを準備
        image_data_for_azure = BytesIO(
            image_data_for_processing.getvalue()
        )

        # Azure Document Intelligenceで画像を解析
        item, analysis_result = make_table_item_from_image(
            image_data_for_azure,
            event=event
        )

        # S3情報をitemに追加
        item.update(s3_info)

        # 解析結果JSONをS3に保存（失敗しても処理継続）
        if analysis_result is not None:
            try:
                json_s3_key = generate_s3_key_for_json(
                    event.source.user_id,
                    event.timestamp,
                    message_id
                )
                logger.info(f"Uploading analysis JSON to S3: {json_s3_key}")

                upload_json_to_s3(
                    analysis_result,
                    json_s3_key,
                    S3_BUCKET_NAME,
                    s3_client
                )
                logger.info(f"Analysis JSON upload successful: {json_s3_key}")

                item['s3_analysis_json_key'] = json_s3_key
            except Exception as json_error:
                logger.error(f"Analysis JSON upload failed: {str(json_error)}")
                item['s3_analysis_json_status'] = 'failed'

        # make a response for LINE bot
        response = makeResponseMessage(item)

        # DynamoDBに登録
        table.put_item(Item=item)

        # 解析結果をユーザーに返信
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=response)
        )

    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="画像の解析中にエラーが発生しました。")
        )


def lambda_handler(event, context):

    '''
        Which function is called, handle_message or handle_image?
        What information is used to judge?

        The judgment is performed inside line-bot-sdk's WebhookHandler.handle().
        It checks each webhook event in request body and dispatches to handlers
        registered by @webhook_handler.add(...), based on event type/message type.

        UML example (Mermaid):
        sequenceDiagram
            participant LINE
            participant Lambda as lambda_handler
            participant WH as WebhookHandler.handle
            participant HM as handle_message
            participant HI as handle_image

            LINE->>Lambda: Webhook event (HTTP request)
            Lambda->>WH: handle(body, signature)
            WH->>WH: verify signature + parse events

            alt message.type == "text"
                WH->>HM: dispatch MessageEvent(TextMessage)
            else message.type == "image"
                WH->>HI: dispatch MessageEvent(ImageMessage)
            end

        The structure of event is described here.
        https://developers.line.biz/ja/reference/messaging-api/#message-event
    '''

    # ヘッダーにx-line-signatureがあることを確認
    if 'x-line-signature' in event['headers']:
        signature = event['headers']['x-line-signature']

    body = event['body']
    # 受け取ったWebhookのJSON
    logger.info(body)

    try:
        # WebhookHandler jedges type of the event from LINE
        # and call corresponding handler(handle_message/handle_image).
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
