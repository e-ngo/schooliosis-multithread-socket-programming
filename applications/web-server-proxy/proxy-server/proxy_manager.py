# This file contains the ProxyManager class which handle all the operations
# done in the proxy-settings page of the project


from cache import * # point of access to cache files

class ProxyManager():
    """
    Manages all the elements from cache and proxy-settings page
    """

    def __init__(self):
        self.init_settings()

    def init_settings (self):
        # Credentials for admins allowed to edit the proxy seetings page
        # append data in the form {'email: email, 'passw': passw}
        self.proxy_admins = []
        self.sites_blocked = []
        # Credentials allowed employees that can browse in private mode
        # append data in the form {'email: email, 'passw': passw}
        self.private_mode_auth = []
        # Credentials  of upper division employess
        # append data in the form {'email: email, 'passw': passw}
        self.managers_credentials = []


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
        return 0


    def list_of_admins(self):
        """
        
        :return: the list of admins
        """
        return 0

    def is_admin(self, email, passw):
        """
        1. get list of admins
        2. check credentials
        :param email: 
        :param passw: 
        :return: true if is admin, otherwise, returns false
        """
        return 0


    def add_site_blocked(self, request):
        """
        Add the blocked site for employees to the self.sites_blocked list
        request: 
        :return: VOID
        """
        return 0

    def get_blocked_site(self, request):
        """
        request: 
        :return: The list of sites blocked for employees
        """

    def is_site_blocked(self, request):
        """
        1. Get all the sites blocked
        2. Check if the url in the request is blocked
        :param request: 
        :return: true if the site is blocked, otherwise, false
        """
        return 0

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
        return 0

    def is_manager(self, email, password):
        """
        Checks if the employee is in the list of upper management 
        employees allowed to browse some special company pages not
        allowed for general employees
        :param email: 
        :param password: 
        :return: True is the employee is upper management, otherwise, returns false
        """
        return 0

    def is_cached(self, request):
        """
        Optional method but really helpful. 
        Checks if a url is already in the cache 
        1. Extract url and private mode status from the request 
        2. Go to cache folder and locate if the resources
           for that url exists in the cache
        request: the request data from the client 
        :return: if the url is cached return true. Otherwise, false
        """
        return 0

    def get_cached_resource(self, request):
        """
        1. Extract url and private mode status from the request 
        2. Go to cache folder and locate if the resources
           for that url exists in the cache
        request: the request data from the client 
        :return: The resource requested
        """
        return 0

    def clear_cache(self):
        """
        
        :return: VOID
        """
        return 0

    def clear_history(self):
        """
        
        :return: VOID
        """
        return 0

    def clear_all(self):
        """
        1. execute clear_cache
        2. execute clear_history
        :return: VOID
        """
        return 0











