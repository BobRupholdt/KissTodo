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
from django.template.loader import get_template
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.conf import settings
from django import forms
from random import choice
from datetime import datetime

import os

if settings.KISSTODO_USE_GAE:
    from google.appengine.api import users
    from google.appengine.api import mail

from models import *

def my_login_required(function):
    def decorated_view(*args, **kwargs):
        
        if settings.KISSTODO_USE_GAE:
            f = function # GAE authentication, nothing to do (see app.yaml)
        else:
            f = login_required(function) # Django authentication
        
        return f(*args, **kwargs)
        
    return decorated_view

def test_page(request):
    if 'op' in request.POST and request.POST['op']=='simulate error':
        raise Exception("Simulated Error!")
    
    return render_to_response('todo/test_page.html', 
        #RequestContext(request, {'media_root':settings.MEDIA_ROOT, 'lists':List.objects, 'todos':Todo.objects,}))
        RequestContext(request, {'media_root':settings.MEDIA_ROOT}))
        
@my_login_required
def board(request, mobile=False, selected_list_id=''):
    inbox = List.objects.get_or_create_inbox(_get_current_user(request))
    
    if settings.KISSTODO_USE_GAE: 
        logout_url=users.create_logout_url(settings.KISSTODO_SITE_URL)
    else:
        logout_url=reverse('logout')
    #login_url=users.create_login_url("/")
        
    #request.session['mobile']=mobile

    return render_to_response('todo/board.html', RequestContext(request, {'inbox_list_id':inbox.id, 'logout_url':logout_url, 'mobile':mobile, 'selected_list_id':selected_list_id}))

def _do_send_mail(t, request):
    address_from = "todo_reminder@"+str(os.environ['APPLICATION_ID'])+".appspotmail.com" 
    address_to = t.list.owner
    if not '@' in address_to: address_to += "@gmail.com"
    subject="KissTodo notification"

    template = get_template('todo/todo_notification_email.txt')
    ctx=RequestContext(request, {'todo':t})

    mail.send_mail(sender=address_from,to=address_to,subject=subject,body=template.render(ctx))

def todo_send_mail(request):
    todos = Todo.objects.filter(notify_todo=True, complete=False, due_date__isnull=False).order_by('due_date')
        
    res = "\nres:\n"
    now = datetime.now() 
    for t in todos: 
        if t.due_date - timedelta(minutes=t.notify_minutes) + timedelta(minutes=t.time_offset)< now:
            res += "\nTODO:"+t.description+"\n"
            _do_send_mail(t, request)
            t.notify_todo=False
            t.save()
        
    return HttpResponse(str(now)+res, mimetype="text/plain") 

@my_login_required
def todo_empty_trash(request):
    for t in Todo.objects.deleted(_get_current_user(request)): t.delete_raw()
    return HttpResponse("", mimetype="text/plain") 
    
@my_login_required
def todo_clear_completed_items(request, list_id):
    l=List.objects.get(id=int(list_id))
    _check_permission(request, l)
    
    todos=Todo.objects.filter(list__id=list_id)
    for t in todos: 
        if t.complete: t.delete_raw()
    
    return HttpResponse("", mimetype="text/plain")     
    
@my_login_required
def todo_search(request, search_string, sort_mode, show_complete='F'):
    todos = Todo.objects.search(_get_current_user(request), search_string)
    
    if (show_complete=='F'):
        todos = [t for t in todos if not t.complete]
        
    return render_to_response('todo/todo_list.html', RequestContext(request, {'todos':Todo.todo_sort(todos, sort_mode), 'show_list': True }))

@my_login_required
def todo_list(request, list_id, sort_mode, show_complete='F', mobile=False):
    #import time
    #time.sleep(1)
    if int(list_id)>0:
        l=List.objects.get(id=int(list_id))
        _check_permission(request, l)
    
    show_list = False
    show_empty_trash = False
    show_clear_completed_items = False
    
    if int(list_id)==-2:
        todos = Todo.objects.hot(_get_current_user(request))
        show_list = True
    elif int(list_id)==-3:
        todos = Todo.objects.deleted(_get_current_user(request))
        show_list = True    
        if len(todos)>0: show_empty_trash = True
    elif int(list_id)==-4:
        todos = Todo.objects.all_by_user(_get_current_user(request))
        show_list = True          
    else:
        todos = Todo.objects.filter(list__id=list_id)
        
    #if (show_complete=='F'):
    #    todos = [t for t in todos if not t.complete]
    
    if int(list_id)>0: show_clear_completed_items=any([t.complete for t in todos])
    
    return render_to_response('todo/todo_list.html', RequestContext(request, {'list_id':list_id,'todos':Todo.todo_sort(todos, sort_mode), 'show_list':show_list, 'show_empty_trash':show_empty_trash, 'show_clear_completed_items':show_clear_completed_items, 'mobile':mobile}))
    
@my_login_required
def list_list(request, selected_list_id, mobile=False):
    inbox = List.objects.get_or_create_inbox(_get_current_user(request))
    return render_to_response('todo/list_list.html', RequestContext(request, {'lists':List.objects.filter(owner=_get_current_user(request)), 'inbox_list': inbox, 'selected_list_id': str(selected_list_id), 'mobile':mobile}))    

@my_login_required
def list_add(request):
    l=List()
    l.name=request.POST['name']
    l.owner=_get_current_user(request)
    if not l.is_special():
        l.save()
        out = l.id
    else:
        out=-1
    return HttpResponse(out, mimetype="text/plain") 
    
@my_login_required
def list_delete(request):
    l=List.objects.get(id=int(request.POST['list_id']))
    _check_permission(request, l)
    l.delete()
    
    return HttpResponse("", mimetype="text/plain")     
    
@my_login_required
def todo_delete(request):
    t=Todo.objects_raw.get(id=int(request.POST['todo_id']))
    _check_permission(request, t.list)
    t.delete()
    return HttpResponse("", mimetype="text/plain")    

@my_login_required    
def todo_undelete(request):
    t=Todo.objects_raw.get(id=int(request.POST['todo_id']))
    _check_permission(request, t.list)
    t.undelete()
    return HttpResponse("", mimetype="text/plain")        
    
@my_login_required
def todo_complete(request):
    t=Todo.objects_raw.get(id=int(request.POST['todo_id']))
    _check_permission(request, t.list)
    
    t.toggle_complete()
    
    t.save()
    
    return HttpResponse("", mimetype="text/plain")  

@my_login_required
def todo_postpone(request):
    t=Todo.objects_raw.get(id=int(request.POST['todo_id']))
    _check_permission(request, t.list)
    t.postpone()
    t.save()
    return HttpResponse("", mimetype="text/plain")        

@my_login_required
def todo_edit(request, todo_id, mobile=False):
    t=Todo.objects_raw.get(id=int(todo_id))
    _check_permission(request, t.list)
    
    if request.method == 'POST':
    
        if 'priority' in request.POST: t.priority=int(request.POST['priority'])
        if 'description' in request.POST: t.description=request.POST['description']
        if 'list_id' in request.POST: t.list=List.objects.get(id=int(request.POST['list_id']))
        if 'due_date' in request.POST: 
            t.due_date=None
            if request.POST['due_date']: 
                try:
                    t.due_date=datetime.strptime(request.POST['due_date'],'%Y/%m/%d %H:%M') # 2012/12/21 15:42
                except:
                    try:
                        t.due_date=datetime.strptime(request.POST['due_date'],'%Y/%m/%d') # 2012/12/21
                    except:
                        try:
                            t.due_date=datetime.strptime(request.POST['due_date'],'%Y-%m-%dT%H:%M') # 2012-12-21T15:42 - for html5 input type
                        except:
                            try:
                                t.due_date=datetime.strptime(request.POST['due_date'],'%Y-%m-%d') # 2012-12-21 - for html5 input type
                            except:
                                pass # wrong format
            
        if 'repeat_type' in request.POST: t.repeat_type=request.POST['repeat_type']
        if 'repeat_every' in request.POST and request.POST['repeat_every']: t.repeat_every=int(request.POST['repeat_every'])
        
        if 'notify_minutes' in request.POST and request.POST['notify_minutes']: t.notify_minutes=int(request.POST['notify_minutes'])
        
        if 'time_offset' in request.POST and request.POST['time_offset']: t.time_offset=int(request.POST['time_offset'])
        
        t.update_notify_todo()

        t.save()
        
        #return render_to_response('todo/todo_item.html', RequestContext(request, {'todo':t,}))    
        return HttpResponseRedirect('/todo/ajax/todo/show_item/'+str(t.id));
    else:
        return render_to_response('todo/todo_edit.html', RequestContext(request, {'todo':t,'repeat_type_choiches':Todo.repeat_type_choiches,'lists':List.objects.filter(owner=_get_current_user(request)), 'mobile':mobile}))

@my_login_required        
def list_edit(request, list_id):
    l=List.objects.get(id=int(list_id))
    _check_permission(request, l)
    
    if request.method == 'POST':
        if 'name' in request.POST: l.name=request.POST['name']
        l.save()
        
        return HttpResponse("", mimetype="text/plain")  
        #return render_to_response('todo/todo_item.html', RequestContext(request, {'todo':t,}))    
    else:
        return render_to_response('todo/list_edit.html', RequestContext(request, {'list':l}))            

@my_login_required
def todo_show_item(request, todo_id, mobile=False):
    t = Todo.objects_raw.get(id=int(todo_id))
    _check_permission(request, t.list)
    return render_to_response('todo/todo_item.html', RequestContext(request, {'todo':t, 'mobile':mobile}))    

@my_login_required    
def todo_add(request):
    l=List.objects.get(id=request.POST['list_id'])
    _check_permission(request, l)
    
    t=Todo()
    t.description=request.POST['description']
    
    for p in range(1,4):
        if t.description[0:2]=="!"+str(p): 
            t.priority=p
            t.description=t.description[2:]

    t.list=l
    t.save()
    out = t.id
    return HttpResponse(out, mimetype="text/plain")     

@my_login_required    
def import_rtm(request):
    if request.method == 'POST':
        
        form = ImportRtmForm(request.POST)
        if not form.is_valid(): return HttpResponse("FORM ERROR", mimetype="text/plain")           
        
        url = form.cleaned_data['url']
        
        if url == "":
            for t in Todo.objects_raw.filter(external_source="ATOM"):
                if t.list.owner==_get_current_user(request): t.delete_raw()
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
            
            t.external_source = "ATOM"
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
                        t.list = _parse_list(c.firstChild.nodeValue, _get_current_user(request))
                    elif field_name == "URL": 
                        t.description += " (%s)" % (c.firstChild.firstChild.nodeValue,)
                    elif field_name == "Repeat every": 
                        t.repeat_every = int(c.firstChild.nodeValue)
                    elif field_name == "Repeat type": 
                        t.repeat_type = _parse_repeat_type(c.firstChild.nodeValue)
                    out += u"\n"
                        
                count+=1
            
            out += t.__unicode__() +"\n"
            out += "\n"
            t.save()
        return HttpResponse(out, mimetype="text/plain")     
    else:
        return render_to_response("todo/import_rtm_form.html",RequestContext(request, {'form': ImportRtmForm()}))  
      
@my_login_required      
def export_atom(request):
   
    list=[]
    
    for t in Todo.objects.filter(complete=False):
        if t.list.owner==_get_current_user(request): list.append(t)
            
    return render_to_response("todo/export_atom.atom",RequestContext(request, {'todos': list}))  # , mimetype="application/atom+xml"
    #return HttpResponse(out, mimetype="text/plain")
    #return HttpResponse(out, mimetype="application/atom+xml")     
           
def cache_manifest(request):
    #import uuid
    #guid=uuid.uuid1()
    return HttpResponse(get_template('todo/cache.manifest').render(RequestContext(request, {'host': request.META.get('HTTP_HOST')})), mimetype="text/cache-manifest")
   
def redirect_login(request):
    return render_to_response("todo/redirect_login.html",RequestContext(request, {}))  
    
def do_logout(request):
    logout(request)
    return HttpResponseRedirect(settings.KISSTODO_SITE_URL)

def _parse_date(date):
    # 'never' or 'Mon 13 Jun 11 18:30' or 'Mon 13 Jun 11'
    
    if date=='never': return None
    
    try:
        dt = datetime.strptime(date, '%a %d %b %y %H:%M')
    except:
        dt = datetime.strptime(date, '%a %d %b %y')
    return dt
    
def _parse_priority(priority):
    # 'none', '1', '2', '3'
    
    if priority=='none': return 4
    return int(priority)
    
def _parse_repeat_type(r):
    # 'none', 'd', 'w', 'm', 'y'
    
    if r=='none': return ''
    return r
    
def _parse_list(list, user):
    if list=='Inbox': 
        return List.objects.get_or_create_inbox(user)
    else:
        list, created = List.objects.get_or_create(name=list, owner=user)
        return list
                        
    return int(priority)     
    
def _check_permission(request, list):
    if list.owner!=_get_current_user(request): raise Exception("Permission denied")
    
def _get_current_user(request):
    if settings.KISSTODO_USE_GAE: 
        user = users.get_current_user()
        if user: return  user.nickname()
    else:
        return request.user.username
    
class ImportRtmForm(forms.Form):
    #text = forms.CharField(widget=forms.Textarea(), label='Atom feed', required=False)
    url = forms.CharField(label='url', required=False)
    