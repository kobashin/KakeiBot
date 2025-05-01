# import functions in line-bot-deployment.funcs
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'line-bot-deployment'))
import requests

line_token = 'q+XLLASki0d76WWa5qaYf1QUyWBs+6XMT63G0DBRq58EKXsSeUZE9bamsJAruQcla0D9AR2eDqgkbHmm3izaxj27HEgbSP2wKyu7jZrFvzf4GTSRw5KhPLj6oWN7S6EWViM8U2E/LBRkzyHAfCHtbgdB04t89/1O/w1cDnyilFU='
channel_secret = '860ca8d2ad16e69c2686cc524612c411'
user_id = 'U55f2c6b5bfc368e349beec673d4dec8a'
message = "毎週月曜日にメッセージを送ります！\n先週使った金額などをお知らせする予定ですが、実装中です...\nしばらくお待ちください..."

headers = {
    "Authorization": f"Bearer {line_token}",
    "Content-Type": "application/json"
}

data = {
    "to": user_id,
    "messages": [
        {
            "type": "text",
            "text": message
        }
    ]
}


# send message
def send_message():
    response = requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers=headers,
        json=data
    )

    return {
        'statusCode': response.status_code,
        'body': response.text
    }


send_message()
