# This file contains the ProxyManager class which handle all the operations
# done in the proxy-settings page of the project


import os.path
import os
import glob
import pickle

BASE_PATH = os.path.abspath(os.path.dirname(__file__))

class ProxyManager:
    """
    Manages all the elements from cache and proxy-settings page
    """

    def __init__(self):
        self.init_settings()

    def init_settings (self):
        # Credentials for admins allowed to edit the proxy seetings page
        # append data in the form {'email: email, 'passw': passw}
        self.proxy_admins = [{'email':'admin@example.com', 'passw':'123'}]
        self.sites_blocked = ['http://youtube.com', 'http://reddit.com']
        # Credentials allowed employees that can browse in private mode
        # append data in the form {'email: email, 'passw': passw}
        self.private_mode_auth = [{'email':'private@example.com', 'passw':'123'}, {'email':'jose@example.com', 'passw':'123'}]
        # Credentials  of upper division employess
        # append data in the form {'email: email, 'passw': passw}
        self.managers_credentials = [{'email':'manager@example.com', 'passw':'123'}]
        self.cached = []
        self.clear_history()


    def add_admin(self, email, passw):
        """
        Adds a new admin to the list of admins that 
        are allowed to edit the proxy settings page
        Creates a python dictionary {'email: email, 'passw': passw} 
        and appends this info to the self.proxy_admins list. 
        :param email: Unique email 
        :param passw: 
        :return: VOID
        """
        self.proxy_admins.append({'email':email, 'passw':passw})

    def list_of_admins(self):
        """
        
        :return: the list of admins
        """
        return self.proxy_admins

    def is_admin(self, email, passw):
        """
        1. get list of admins
        2. check credentials
        :param email: 
        :param passw: 
        :return: true if is admin, otherwise, returns false
        """
        admin_list = self.list_of_admins()
        for admin in admin_list:
            try:
                return admin[email] == passw
            except KeyError:
                pass
        return False

    def add_site_blocked(self, url):
        """
        Add the blocked site for employees to the self.sites_blocked list
        url: 
        :return: VOID
        """
        self.sites_blocked.append(url)

    def get_blocked_site(self, request):
        """
        request: 
        :return: The list of sites blocked for employees
        """
        return self.sites_blocked

    def is_site_blocked(self, url):
        """
        1. Get all the sites blocked
        2. Check if the url in the url is blocked
        :param url: 
        :return: true if the site is blocked, otherwise, false
        """
        for site in self.sites_blocked:
            if site == url:
                return True
        return False

    def add_manager(self, email, password):
        """
        Adds a new employee with auth to browse in some company resources 
        that are not allowed for general employees.
        Creates a python dictionary {'email: email, 'passw': passw} 
        and appends this info to the self.managers_credentials list. 
        :param email: Unique email 
        :param password: 
        :return: 
        """
        self.managers_credentials.append({'email':email, 'passw':passw})

    def is_manager(self, email, password):
        """
        Checks if the employee is in the list of upper management 
        employees allowed to browse some special company pages not
        allowed for general employees
        :param email: 
        :param password: 
        :return: True is the employee is upper management, otherwise, returns false
        """
        manager_list = self.managers_credentials
        for manager in manager_list:
            try:
                return manager[email] == passw
            except KeyError:
                pass
        return False

    def update_cache(self, url, response):
        """
        Adds element into cache.
        :param url: used as hash
        :param response: response object to save
        """
        path = os.path.abspath(os.path.dirname(__file__))
        with open("{}/cache/resources/{}.pickle".format(BASE_PATH, url), "wb") as file_handle:
            pickle.dump(response, file_handle, protocol=pickle.HIGHEST_PROTOCOL)
        if not self.is_cached(url):
            self.cache.append(url)
    def is_cached(self, url):
        """
        Optional method but really helpful. 
        Checks if a url is already in the cache 
        1. Extract url and private mode status from the request 
        2. Go to cache folder and locate if the resources
           for that url exists in the cache
        request: the request data from the client 
        :return: if the url is cached return true. Otherwise, false
        """
        for i in self.cached:
            if i == url:
                return True
        return False
        # return os.path.exists("{}/cache/resources/{}.pickle".format(BASE_PATH,url))

    def get_cached_resource(self, url):
        """
        1. Extract url and private mode status from the request 
        2. Go to cache folder and locate if the resources
           for that url exists in the cache
        request: the request data from the client 
        :return: The resource requested
        """
        with open("{}/cache/resources/{}.pickle".format(BASE_PATH, url), "rb") as file_handle:
            s = pickle.load(file_handle)
        return s

    def clear_cache(self):
        """
        
        :return: VOID
        """
        files = glob.glob('{}/cache/resources/*.pickle'.format(BASE_PATH))
        for f in files:
            os.remove(f)
        self.cached = []
    
    def get_history(self):
        """
        Get history list from ./cache/history.pickle
        """
        with open("{}/cache/history.pickle".format(BASE_PATH), "rb") as file_handle:
            s = pickle.load(file_handle)
        return s
    
    def add_history(self, url):
        """
        Adds to history
        :return: VOID
        """
        history_list = self.get_history()
        history_list.append(url)
        with open("{}/cache/history.pickle".format(BASE_PATH), "wb") as file_handle:
            pickle.dump(history_list, file_handle, protocol=pickle.HIGHEST_PROTOCOL)

    def clear_history(self):
        """
        
        :return: VOID
        """
        with open("{}/cache/history.pickle".format(BASE_PATH), "wb") as file_handle:
            pickle.dump([], file_handle, protocol=pickle.HIGHEST_PROTOCOL)

    def clear_all(self):
        """
        1. execute clear_cache
        2. execute clear_history
        :return: VOID
        """
        self.clear_cache()
        self.clear_history()











if __name__=="__main__":
    path = os.path.abspath(os.path.dirname(__file__))
    # print(path)
    # print(path+'/pickle')