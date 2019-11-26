from datetime import datetime
class Logging(object):
    def __init__(self):
        self.verbose_logging = True
        self.log_level_map = {
            0: 'INFO    ', 
            1: 'ERROR   ', 
            2: 'CRITICAL', 
            3: 'FATAL   '
            }
    
    def log(self, origin, message, log_level = 0, err = ""): # 0 = info, 1 = error, 2 = critical, 3 = fatal
        if self.verbose_logging:
            try:
               self.log_to_file(str(origin), str(message) + str(err), self.log_level_map[log_level])
            except KeyError as e:
               self.log_to_file(str(origin), str(message) + str(err), 'ERROR')

    def log_to_file(self, origin, body, log_level):
        time_stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f = open("log.txt", "a")
        f.write(log_level + " | " + origin + " | " + body + " |" + time_stamp + "\n")
        f.close()