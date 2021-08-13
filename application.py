from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
import os
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    FlexSendMessage
)
import json

app = Flask(__name__)

# @app.route("/")
# def hello():
#     "hello world"
#     return "Hello World!!!!!"

LINE_SECRET = os.getenv("Line_secret")
LINE_TOKEN = os.getenv("Line_token")
LINE_BOT = LineBotApi(LINE_TOKEN)
HANDLER = WebhookHandler(LINE_SECRET)

@app.route("/callback", methods=["POST"])
def callback():
    # X-Line-Signature: 數位簽章
    signature = request.headers["X-Line-Signature"]
    print(signature)
    body = request.get_data(as_text=True)
    print(body)
    try:
        HANDLER.handle(body, signature)
    except InvalidSignatureError:
        print("Check the channel secret/access token.")
        abort(400)
    return "OK"

# message 可以針對收到的訊息種類
@HANDLER.add(MessageEvent, message=TextMessage)
def handle_message(event):

    url_dict = {
      "TIBAME":"https://www.tibame.com/coursegoodjob/traffic_cli", 
      "HELP":"https://developers.line.biz/zh-hant/docs/messaging-api/",
      "YOUTUBE":"https://www.youtube.com/"}
    # 將要發出去的文字變成TextSendMessage
    if event.message.text.upper() in url_dict.keys():
        url = url_dict[event.message.text.upper()]
        message = TextSendMessage(text=url)
        LINE_BOT.reply_message(event.reply_token, message)

    elif event.message.text,upper() == "WISDOM":
        with open("templates/flex_test.json", "r") as f_r:
            bubble = json.load(f_r)
        f_r.close()
        LINE_BOT.reply_message(
            event.reply_token,
            [FlexSendMessage(alt_text="Report", contents=bubble)]
        )
    else:
        message = TextSendMessage(text=event.message.text)
        # 回覆訊息
        LINE_BOT.reply_message(event.reply_token, message)
