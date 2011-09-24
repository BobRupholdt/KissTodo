from django.http import HttpResponseRedirect

class AjaxMiddleware(object):
    def process_response(self, request, response):
        if request.is_ajax():
            if type(response) == HttpResponseRedirect or response.status_code == 302:
                response.status_code = 278
        return response
