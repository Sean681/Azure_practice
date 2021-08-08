from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
app = Flask(__name__)

# @app.route("/")
# def hello():
#     "hello world"
#     return "Hello World!!!!!"

LINE_SECRET = "6d024ea68b260782527596c92c443698"]
LINE_TOKEN = "i+oLN4OdIOM4KdzooU2ydtVCEcRpS3pNoGeVxe0K1fkiBNwZmfMpnxbbIVW+2iatPzv0bSzmwInx/5u5ijXZcMHXdxS8h8uP+uC1ASzsUp2Wj3i1BIp+d1dAyRXisyPmFzqpgSehJj59/Do3bX2z8QdB04t89/1O/w1cDnyilFU="
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
