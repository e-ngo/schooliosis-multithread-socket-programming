from flask import Flask, render_template, request, redirect, Response
import requests
from client.client import Client
from proxy_server.proxy_manager import ProxyManager

app = Flask(__name__)


@app.route('/')
def home():
   return render_template('home.html')

@app.route('/proxy-settings')
def proxy_settings():
    pm = ProxyManager()
    admins = pm.list_of_admins()
    managers = pm.managers_credentials
    blocked_sites = pm.sites_blocked
    history = pm.get_history()
    cache = pm.cached
    private_mode_users = pm.private_mode_auth
    
    return render_template('proxy-settings.html', admins=admins,managers=managers,blocked_sites=blocked_sites,history=history, cache=cache, private_mode_users=private_mode_users)

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
    data = {'url': url, 'is_private_mode': is_private_mode, 'client_ip':request.remote_addr, 'http_version': request.environ.get('SERVER_PROTOCOL')}
    client.request_to_proxy(data)
    res = client.response_from_proxy()
    # reseponse_from_proxy....
    # Flask.make_response()
    # response = Flask.HTTPResponse(client.reseponse_from_proxy())
    # response.begin()
    # return response.get_content()
    # response_object = Flask.make_response(res)
    # print(response_object)
    # auth
    # res = Response(res)
    html_body = res.split("\r\n")[-1]
    return html_body

if __name__ == '__main__':
    app.run()
