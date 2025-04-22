import os

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for, abort)

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import PostbackEvent, TextSendMessage, MessageEvent, TextMessage

app = Flask(__name__)

TOKEN = os.environ.get('LINE_TOKEN', None)
SECRET = os.environ.get('LINE_SECRET', None)

line_bot_api = LineBotApi(TOKEN)
whhandler = WebhookHandler(SECRET)

@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello', methods=['POST'])
def hello():
   name = request.form.get('name')

   if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))

@app.route('/callback', methods=['POST'])
def callback():
    # 確認請求來自 LINE
    signature = request.headers['X-Line-Signature']

    # 獲取請求主體
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    try:
        whhandler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@whhandler.add(MessageEvent,message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=str(f'{event}')))

@app.route('/hi',methods=['get'])
def hi():
    return TOKEN

if __name__ == '__main__':
   app.run()
