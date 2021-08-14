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
from datetime import datetime, timezone, timedelta
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials

app = Flask(__name__)

# @app.route("/")
# def hello():
#     "hello world"
#     return "Hello World!!!!!"

LINE_SECRET = os.getenv("Line_secret")
LINE_TOKEN = os.getenv("Line_token")
LINE_BOT = LineBotApi(LINE_TOKEN)
HANDLER = WebhookHandler(LINE_SECRET)
# Face_recognition
Face_client_key = os.getnev("FACE_CLIENT_KEY")
Face_client_endpoint = os.getnev("FACE_CLIENT_ENDPOINT")
FACE_CLIENT = FaceClient(
  Face_client_endpoint, CognitiveServicesCredentials(Face_client_key))

@app.route("/")
def hello():
    "hello world"
    return "Hello World!!!!!"


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
      "YOUTUBE":"https://www.youtube.com/",
      "TEST":"https://www.planetsport.com/image-library/square/500/r/ronaldo-roma-2021.jpg"}
# 將要發出去的文字變成TextSendMessage
    if event.message.text.upper() in url_dict.keys():
        url = url_dict[event.message.text.upper()]
        message = TextSendMessage(text=url)

    elif event.message.text.upper() == "WISDOM":
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

# 與Line Messaging API結合
@HANDLER.add(MessageEvent, message=ImageMessage)
def handler_content_message(event):
    # 先把傳來的照片存檔
    filename = f"{event.message.id}.jpg"
    message_content = LINE_BOT.get_message_content(
        event.message.id
    )
    with open(filename, "wb") as f_w:
        for chunk in message_content.iter_content():
            f_w.write(chunk)
    f_w.close()
    
    name = azure_face_recognition(filename)
    # 若有一張人臉，輸出人臉辨識結果
    if name != "":
        now = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M")
        output = f"{name}, {now}"
    else:
        output = "NOTHING"

    LINE_BOT.reply_message(event.reply_token, output)


def azure_face_recognition(filename):
    img = open(filename, "r+b")
    detected_face = FACE_CLIENT.face.detect_with_stream(
        img, detection_model="detection_01"
    )
    
    if len(detected_face) != 1:
        return ""
    
    results = FACE_CLIENT.face.identify([detected_face[0].face_id], PERSON_GROUP_ID)
    
    if len(results) == 0:
        return "unknown"
    
    result = results[0].as_dict()
    # 找不到相像的人
    if result["candidates"][0]["confidence"] < 0.5:
        return "unknown"
    person = FACE_CLIENT.person_group_person.get(
        PERSON_GROUP_ID, result["candidates"][0]["person_id"]
    )
    
    return person.name
