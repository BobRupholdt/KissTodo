from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.conf import settings
from random import choice

from models import *
  
def test_page(request):
    if 'op' in request.POST and request.POST['op']=='create list':
        new_list=List(name=request.POST['add'])
        new_list.save()
        return HttpResponseRedirect(reverse(test_page))
        
    if 'op' in request.POST and request.POST['op']=='create todo':
        new_todo=Todo()
        new_todo.priority = 1
        new_todo.list = choice(List.objects.all())
        new_todo.description=request.POST['add']
        new_todo.save()
        return HttpResponseRedirect(reverse(test_page))
        
    if 'op' in request.POST and request.POST['op']=='clear data':
        for tl in List.objects.all(): tl.delete()
        for t in Todo.objects.all(): t.delete()
        return HttpResponseRedirect(reverse(test_page))    

    if 'op' in request.POST and request.POST['op']=='simulate error':
        raise Exception("Error!")
    
    return render_to_response('todo/test_page.html', 
        RequestContext(request, {'media_root':settings.MEDIA_ROOT, 'lists':List.objects, 'todos':Todo.objects,}))

def board(request):
    return render_to_response('todo/board.html', 
        RequestContext(request, {'lists':List.objects,}))
    
def todo_list(request, list_id):
    return render_to_response('todo/todo_list.html', RequestContext(request, {'todos':Todo.objects.filter(list__id=list_id)}))
