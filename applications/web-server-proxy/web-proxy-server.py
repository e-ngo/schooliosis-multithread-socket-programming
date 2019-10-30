from flask import Flask, render_template, request, redirect, Response
import requests
from client.client import Client
from proxy_server.proxy_manager import ProxyManager

app = Flask(__name__)


@app.route('/')
def home():
   return render_template('home.html')

@app.route('/proxy-settings', methods=['GET', 'POST'])
def proxy_settings():
    print("Something...")
    pm = ProxyManager()

    if request.method == 'POST':
        if request.form.get('addnewadmin') == 'True':
            new_manager = request.form.get('admins')
            s = new_manager.split(':')
            if len(s) == 2:
                pm.add_admin(s[0], s[1])
        if request.form.get('addblockedsite') == 'True':
            new_blocked_site = request.form.get('blocked_sites')
            if new_blocked_site != "":
                pm.add_site_blocked(new_blocked_site)
        if request.form.get('adduser') == 'True':
            new_admin = request.form.get('private_mode_users')
            s = new_admin.split(':')
            if len(s) == 2:
                pm.add_private_mode_user(s[0], s[1])
        if request.form.get('addmanager') == 'True':
            new_private_mode_user = request.form.get('managers')
            s = new_private_mode_user.split(':')
            if len(s) == 2:
                pm.add_manager(s[0], s[1])
        if request.form.get('clearcache') == 'True':
            # clear cache
            pm.clear_cache()
    admins = pm.list_of_admins()
    managers = pm.managers_credentials
    blocked_sites = pm.sites_blocked
    history = pm.get_history()
    cache = pm.get_cache()
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
  
    html_body = res.split("\r\n")[-1]
    return html_body

if __name__ == '__main__':
    app.run()
