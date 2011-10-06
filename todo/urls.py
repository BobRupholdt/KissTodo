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

from django.conf.urls.defaults import *

from todo.views import *

urlpatterns = patterns('',
    (r'^test_page$', test_page),
    url(r'^board$', board, {}, "board"),
    url(r'^ajax/list/list/(?P<selected_list_id>.*)$', list_list, {}, "list_list"),
    (r'^ajax/list/add/$', list_add),
    (r'^ajax/list/delete/$', list_delete),
    (r'^ajax/list/edit/(?P<list_id>.*)$', list_edit),
    url(r'^ajax/todo/list/(?P<list_id>.+)/(?P<sort_mode>.+)/(?P<show_complete>.+)$', todo_list, name='todo_list_complete'),
    (r'^ajax/todo/list/(?P<list_id>.+)/(?P<sort_mode>.+)$', todo_list),
    (r'^ajax/todo/search/(?P<search_string>.+)/(?P<sort_mode>.+)/(?P<show_complete>.+)$', todo_search),
    (r'^ajax/todo/add/$', todo_add),
    (r'^ajax/todo/delete/$', todo_delete),
    (r'^ajax/todo/undelete/$', todo_undelete),
    (r'^ajax/todo/complete/$', todo_complete),
    (r'^ajax/todo/postpone/$', todo_postpone),
    url(r'^ajax/todo/edit/(?P<todo_id>.*)$', todo_edit, {}, "todo_edit"),
    (r'^ajax/todo/show_item/(?P<todo_id>.*)$', todo_show_item),
    (r'^ajax/todo/empty_trash/$', todo_empty_trash),
    
    url(r'^mboard$', board, {'mobile': True}, "mobile_board"),
    url(r'^majax/list/list/(?P<selected_list_id>.*)$', list_list, {'mobile':True}, "mobile_list_list"),
    url(r'^majax/todo/edit/(?P<todo_id>.*)$', todo_edit, {'mobile':True}, "mobile_todo_edit"),
    
    (r'^import/rtm$', import_rtm),
    (r'^export/atom$', export_atom),
    (r'^send_mail$', todo_send_mail),
    (r'^redirect_login$', redirect_login),
    
)



