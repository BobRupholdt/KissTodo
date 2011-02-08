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
    (r'^board$', board),
    (r'^ajax/todo_list/(?P<list_id>.*)', todo_list),
    (r'^ajax/list_list/(?P<selected_list_id>.*)', list_list),
    (r'^ajax/add_list/$', add_list),
    (r'^ajax/add_todo/$', add_todo),
)



