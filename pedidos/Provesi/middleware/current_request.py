import threading

thread_local = threading.local()

def get_current_request():
    return getattr(thread_local, "request", None)


class CurrentRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        thread_local.request = request
        response = self.get_response(request)
        return response