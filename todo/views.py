# KissTodo - a simple, Django based todo management tool.
# Copyright (C) 2011 Massimo Barbieri - http://www.massimobarbieri.it
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
    #if 'op' in request.POST and request.POST['op']=='clear data':
    #    for tl in List.objects.all(): tl.delete()
    #    for t in Todo.objects.all(): t.delete()
    #    return HttpResponseRedirect(reverse(test_page))    

    if 'op' in request.POST and request.POST['op']=='simulate error':
        raise Exception("Simulated Error!")
    
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

def list_add(request):
    l=List()
    l.name=request.POST['name'];
    l.save()
    out = l.id
    return HttpResponse(out, mimetype="text/plain") 
    
def list_delete(request):
    
    l=List.objects.get(id=int(request.POST['list_id']))
    
    if l.name=="@inbox":
        for t in l.todo_set.all(): t.delete()
    elif len(l.todo_set.all())>0:
        inbox_list=List.objects.filter(name="@inbox")
        if len(inbox_list)==0:
            inbox_list=List(name="@inbox")
            inbox_list.save()
        for t in l.todo_set.all(): 
            t.list=inbox_list
            t.save()
            
    l.delete()
    return HttpResponse("", mimetype="text/plain")     
    
def todo_delete(request):
    t=Todo.objects.get(id=int(request.POST['todo_id']))
    t.delete()
    return HttpResponse("", mimetype="text/plain")    
    
def todo_complete(request):
    t=Todo.objects.get(id=int(request.POST['todo_id']))
    t.complete=not t.complete
    t.save()
    return HttpResponse("", mimetype="text/plain")    

def todo_edit(request, todo_id):
    if request.method == 'POST':
        t=Todo.objects.get(id=int(todo_id))
    
        if 'priority' in request.POST: t.priority=int(request.POST['priority'])
        if 'description' in request.POST: t.description=request.POST['description']
        t.save()
        
        #return HttpResponse("", mimetype="text/plain")  
        return render_to_response('todo/todo_item.html', RequestContext(request, {'todo':t,}))    
    else:
        return render_to_response('todo/todo_edit.html', RequestContext(request, {'todo':Todo.objects.get(id=int(todo_id)),}))
        
def list_edit(request, list_id):
    if request.method == 'POST':
        l=List.objects.get(id=int(list_id))
    
        if 'name' in request.POST: l.name=request.POST['name']
        l.save()
        
        return HttpResponse("", mimetype="text/plain")  
        #return render_to_response('todo/todo_item.html', RequestContext(request, {'todo':t,}))    
    else:
        return render_to_response('todo/list_edit.html', RequestContext(request, {'list':List.objects.get(id=int(list_id)),}))            

def todo_show_item(request, todo_id):
    return render_to_response('todo/todo_item.html', RequestContext(request, {'todo':Todo.objects.get(id=int(todo_id)),}))    
    
def todo_add(request):
    l=List.objects.get(id=request.POST['list_id'])
    t=Todo()
    t.description=request.POST['description']
    t.list=l
    t.save()
    out = t.id
    return HttpResponse(out, mimetype="text/plain")     