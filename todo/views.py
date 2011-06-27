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
from django import forms
from random import choice
from google.appengine.api import users
from datetime import datetime


from models import *
  
def test_page(request):
    if 'op' in request.POST and request.POST['op']=='simulate error':
        raise Exception("Simulated Error!")
    
    return render_to_response('todo/test_page.html', 
        #RequestContext(request, {'media_root':settings.MEDIA_ROOT, 'lists':List.objects, 'todos':Todo.objects,}))
        RequestContext(request, {'media_root':settings.MEDIA_ROOT}))

def board(request):
    inbox = List.objects.get_or_create_inbox(_get_current_user())
    return render_to_response('todo/board.html', RequestContext(request, {'inbox_list_id':inbox.id}))
    
def todo_list(request, list_id, sort_mode, show_complete='F'):
    #import time
    #time.sleep(1)
    if int(list_id)>0:
        l=List.objects.get(id=int(list_id))
        _check_permission(l)
    
    show_list = False
    
    if int(list_id)==-2:
        todos = Todo.objects.hot(_get_current_user())
        show_list = True
    elif int(list_id)==-3:
        todos = Todo.objects.deleted(_get_current_user())
        show_list = True    
    else:
        todos = Todo.objects.filter(list__id=list_id)
        
    if (show_complete=='F'):
        todos = [t for t in todos if not t.complete]
        
    #if show_complete is None: show_complete="N-A"
    #return HttpResponse("***"+show_complete+"***", mimetype="text/plain")      
    return render_to_response('todo/todo_list.html', RequestContext(request, {'list_id':list_id,'todos':Todo.todo_sort(todos, sort_mode), 'show_list':show_list}))
    
def list_list(request, selected_list_id):
    inbox = List.objects.get_or_create_inbox(_get_current_user())
    return render_to_response('todo/list_list.html', RequestContext(request, {'lists':List.objects.filter(owner=_get_current_user()), 'inbox_list': inbox, 'selected_list_id': str(selected_list_id)}))    

def list_add(request):
    l=List()
    l.name=request.POST['name']
    l.owner=_get_current_user()
    if not l.is_special():
        l.save()
        out = l.id
    else:
        out=-1
    return HttpResponse(out, mimetype="text/plain") 
    
def list_delete(request):
    l=List.objects.get(id=int(request.POST['list_id']))
    _check_permission(l)
    l.delete()
    
    return HttpResponse("", mimetype="text/plain")     
    
def todo_delete(request):
    t=Todo.objects_raw.get(id=int(request.POST['todo_id']))
    _check_permission(t.list)
    t.delete()
    return HttpResponse("", mimetype="text/plain")    
    
def todo_undelete(request):
    t=Todo.objects_raw.get(id=int(request.POST['todo_id']))
    _check_permission(t.list)
    t.undelete()
    return HttpResponse("", mimetype="text/plain")        
    
def todo_complete(request):
    t=Todo.objects_raw.get(id=int(request.POST['todo_id']))
    _check_permission(t.list)
    
    t.toggle_complete()
    
    t.save()
    
    return HttpResponse("", mimetype="text/plain")  

def todo_postpone(request):
    t=Todo.objects_raw.get(id=int(request.POST['todo_id']))
    _check_permission(t.list)
    t.postpone()
    t.save()
    return HttpResponse("", mimetype="text/plain")        

def todo_edit(request, todo_id):
    t=Todo.objects_raw.get(id=int(todo_id))
    _check_permission(t.list)
    
    if request.method == 'POST':
    
        if 'priority' in request.POST: t.priority=int(request.POST['priority'])
        if 'description' in request.POST: t.description=request.POST['description']
        if 'list_id' in request.POST: t.list=List.objects.get(id=int(request.POST['list_id']))
        if 'due_date' in request.POST: 
            t.due_date=None
            if request.POST['due_date']: t.due_date=datetime.strptime(request.POST['due_date'],'%Y/%m/%d')
            
        if 'repeat_type' in request.POST: t.repeat_type=request.POST['repeat_type']
        if 'repeat_every' in request.POST and request.POST['repeat_every']: t.repeat_every=int(request.POST['repeat_every'])
        

        t.save()
        
        #return HttpResponse("", mimetype="text/plain")  
        return render_to_response('todo/todo_item.html', RequestContext(request, {'todo':t,}))    
    else:
        return render_to_response('todo/todo_edit.html', RequestContext(request, {'todo':t,'repeat_type_choiches':Todo.repeat_type_choiches,'lists':List.objects.filter(owner=_get_current_user())}))
        
def list_edit(request, list_id):
    l=List.objects.get(id=int(list_id))
    _check_permission(l)
    
    if request.method == 'POST':
        if 'name' in request.POST: l.name=request.POST['name']
        l.save()
        
        return HttpResponse("", mimetype="text/plain")  
        #return render_to_response('todo/todo_item.html', RequestContext(request, {'todo':t,}))    
    else:
        return render_to_response('todo/list_edit.html', RequestContext(request, {'list':l}))            

def todo_show_item(request, todo_id):
    t = Todo.objects_raw.get(id=int(todo_id))
    _check_permission(t.list)
    return render_to_response('todo/todo_item.html', RequestContext(request, {'todo':t}))    
    
def todo_add(request):
    l=List.objects.get(id=request.POST['list_id'])
    _check_permission(l)
    
    t=Todo()
    t.description=request.POST['description']
    t.list=l
    t.save()
    out = t.id
    return HttpResponse(out, mimetype="text/plain")     
    
def import_rtm(request):
    if request.method == 'POST':
        
        form = ImportRtmForm(request.POST)
        if not form.is_valid(): return HttpResponse("FORM ERROR", mimetype="text/plain")           
        
        url = form.cleaned_data['url']
        
        if url == "":
            for t in Todo.objects_raw.filter(external_source="RememberTheMilk"):
                if t.list.owner==_get_current_user(): t.delete_raw()
            return HttpResponse("Empty atom feed received. Cleanup complete.", mimetype="text/plain")  
            
        import urllib2
        text = urllib2.urlopen(url).read()
        #return HttpResponse(text, mimetype="text/plain")             
        
        from xml.dom import minidom
        from datetime import datetime
        
        #xmldoc = minidom.parseString(text.encode( "utf-8" ))
        xmldoc = minidom.parseString(text)
        entries=xmldoc.getElementsByTagName("entry")
        
        out=""
            
        for e in entries: 
        
            t = Todo()
            t.description = e.getElementsByTagName("title")[0].firstChild.nodeValue
            t.deleted = False
            t.completed = False
            
            t.external_source = "RememberTheMilk"
            t.external_id = e.getElementsByTagName("id")[0].firstChild.nodeValue

            out += 'external_id: "'+e.getElementsByTagName("id")[0].firstChild.nodeValue+'"\n'
            out += "title: "+e.getElementsByTagName("title")[0].firstChild.nodeValue+"\n"
    
            count=0
            field_name = ""
            for c in e.getElementsByTagName("content")[0].getElementsByTagName("span"):
                #out += ('"'+(c.firstChild.nodeValue or u"*")+'" ')
                if count % 2 == 0: 
                    field_name = str(c.firstChild.nodeValue).strip()[0:-1]
                else:
                    out += '"%s"=>"%s"' % (field_name, c.firstChild.nodeValue)
                    
                    if field_name == "Due": 
                        t.due_date = _parse_date(c.firstChild.nodeValue)
                    elif field_name == "Priority": 
                        t.priority = str(_parse_priority(c.firstChild.nodeValue))
                    elif field_name == "List": 
                        t.list = _parse_list(c.firstChild.nodeValue, _get_current_user())
                    out += u"\n"
                        
                count+=1
            
            out += t.__unicode__() +"\n"
            out += "\n"
            t.save()
        return HttpResponse(out, mimetype="text/plain")     
    else:
        return render_to_response("todo/import_rtm_form.html",RequestContext(request, {'form': ImportRtmForm()}))  

def _parse_date(date):
    # 'never' or 'Mon 13 Jun 11 at 8:30AM' or 'Mon 13 Jun 11'
    
    if date=='never': return None
    
    try:
        dt = datetime.strptime(date, '%a %d %b %y at %I:%M%p')
    except:
        dt = datetime.strptime(date, '%a %d %b %y')
    return dt
    
def _parse_priority(priority):
    # 'none', '1', '2', '3'
    
    if priority=='none': return 4
    return int(priority)
    
def _parse_list(list, user):
    if list=='Inbox': 
        return List.objects.get_or_create_inbox(user)
    else:
        list, created = List.objects.get_or_create(name=list, owner=_get_current_user())
        return list
                        
    return int(priority)     
def _check_permission(list):
    if list.owner!=_get_current_user(): raise Exception("Permission denied")
    
def _get_current_user():
    user = users.get_current_user()
    if user: return  user.nickname()
    return '[anonymous user]'
    
class ImportRtmForm(forms.Form):
    #text = forms.CharField(widget=forms.Textarea(), label='Atom feed', required=False)
    url = forms.CharField(label='url', required=False)
    