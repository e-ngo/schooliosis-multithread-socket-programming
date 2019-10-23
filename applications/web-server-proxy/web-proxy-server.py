from flask import Flask
from flask import Flask, render_template, request, redirect
import requests
from client.client import Client

app = Flask(__name__)


@app.route('/')
def home():
   return render_template('home.html')

@app.route('/proxy-settings')
def proxy_settings():
    return render_template('proxy-settings.html')

@app.route('/home.html', methods=['POST'])
def get_user_input():
    url = request.form.get('url')
    is_private_mode = 0
    if request.form.get('private'):
        is_private_mode = 1
    if "proxy-settings" in url:
        return proxy_settings()

    # makes new client. request_to_proxy....
    client = Client()
    data = {'url': url, 'is_private_mode': is_private_mode, 'client_ip':request.remote_addr}
    client.request_to_proxy(data)
    res = client.response_from_proxy()
    print("Response from client is ", res)
    # reseponse_from_proxy....
    # Flask.make_response()
    # response = Flask.HTTPResponse(client.reseponse_from_proxy())
    # response.begin()
    # return response.get_content()
    response_object = Flask.make_response(res)
    print(response_object)
    return res

if __name__ == '__main__':
    app.run()
