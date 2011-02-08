from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.http import HttpResponse
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
    #import time
    #time.sleep(1)
    return render_to_response('todo/todo_list.html', RequestContext(request, {'list_id':list_id,'todos':Todo.objects.filter(list__id=list_id)}))
    
def list_list(request, selected_list_id):
    return render_to_response('todo/list_list.html', RequestContext(request, {'lists':List.objects.all(), 'selected_list_id': str(selected_list_id)}))    

def add_list(request):
    l=List()
    l.name=request.POST['name'];
    l.save()
    out = l.id
    return HttpResponse(out, mimetype="text/plain") 
    
def add_todo(request):
    l=List.objects.get(id=request.POST['list_id'])
    t=Todo()
    t.description=request.POST['description']
    t.list=l
    t.save()
    out = t.id
    return HttpResponse(out, mimetype="text/plain")     