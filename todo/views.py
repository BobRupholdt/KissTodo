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
    
def list_todo(request, list_id):
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
    
def delete_list(request):
    l=List.objects.get(id=int(request.POST['list_id']))
    l.delete()
    return HttpResponse("", mimetype="text/plain")     
    
def delete_todo(request):
    t=Todo.objects.get(id=int(request.POST['todo_id']))
    t.delete()
    return HttpResponse("", mimetype="text/plain")    
    
def complete_todo(request):
    t=Todo.objects.get(id=int(request.POST['todo_id']))
    t.complete=not t.complete
    t.save()
    return HttpResponse("", mimetype="text/plain")        
    
def add_todo(request):
    l=List.objects.get(id=request.POST['list_id'])
    t=Todo()
    t.description=request.POST['description']
    t.list=l
    t.save()
    out = t.id
    return HttpResponse(out, mimetype="text/plain")     