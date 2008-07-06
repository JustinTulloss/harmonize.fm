import time
import logging
log = logging.getLogger(__name__)
class TimerApp:
    def __init__(self, application, app_conf):
        self.application = application

    def __call__(self, environ, start_response):
        start = time.time()
        def measure_time(status, response_headers, exc_info=None):
            response = start_response(status, response_headers, exc_info)
            log.info('Request for %s took %f milliseconds', 
                environ['PATH_INFO'], (time.time()-start)*1000)
            return response

        return self.application(environ, measure_time)
