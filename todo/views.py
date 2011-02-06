from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from django.conf import settings

from models import *

#@login_required    
def test_page(request):

    if 'add' in request.POST:
        new_list=TodoList(name=request.POST['add'])
        new_list.save()
        return HttpResponseRedirect(reverse(test_page))
    
    return render_to_response('todo/test_page.html', RequestContext(request, {'media_root':settings.MEDIA_ROOT, 'todo_lists':TodoList.objects}))
