from flask import Flask, render_template, request, redirect, Response
import requests
from client.client import Client
from proxy_server.proxy_manager import ProxyManager

app = Flask(__name__)

# singleton
# try:
#     client
# except NameError:
#     client = Client()

@app.route('/')
def home():
   return render_template('home.html')

@app.route('/proxy-settings', methods=['GET', 'POST'])
def proxy_settings():
    pm = ProxyManager()
    # parse form for new changes. Note that because admin, manager, and private_mode_user credentials are hard-coded,
    # manually update the ProxyManager's init code.
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
        if request.form.get('clearhistory') == 'True':
            # clear cache
            pm.clear_history()
    # get proxy manager settings
    admins = pm.list_of_admins()
    managers = pm.managers_credentials
    blocked_sites = pm.sites_blocked
    history = pm.get_history()
    cache = pm.get_cache()
    private_mode_users = pm.private_mode_auth
    
    return render_template('proxy-settings.html', admins=admins,managers=managers,blocked_sites=blocked_sites,history=history, cache=cache, private_mode_users=private_mode_users)

@app.route('/home.html', methods=['POST'])
def get_user_input():
    client = Client()
    email = request.form.get('email') or ""
    password = request.form.get('password') or ""
    url = request.form.get('url') or ""
    is_private_mode = 0
    if request.form.get('private'):
        is_private_mode = 1
    if "proxy-settings" in url:
        return proxy_settings()
    # if private mode selected or email or password is passed in...
    if is_private_mode == 1 or ( email != "" or password != "" ):
        data = {'url': url, 'is_private_mode': is_private_mode, 'client_ip':request.remote_addr, 'http_version': request.environ.get('SERVER_PROTOCOL'), 'user_name': email, 'password': password}
    else:
        # makes new client. request_to_proxy....
        data = {'url': url, 'is_private_mode': is_private_mode, 'client_ip':request.remote_addr, 'http_version': request.environ.get('SERVER_PROTOCOL')}

    client.request_to_proxy(data)
    res = client.response_from_proxy()

    html_body = res.split("\r\n")[-1]
    return html_body

if __name__ == '__main__':
    app.run()
