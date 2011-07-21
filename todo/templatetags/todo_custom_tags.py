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

from google.appengine.api import users
from django import template
import app_version

register = template.Library()

@register.simple_tag
def app_version_info():
    return app_version.APP_VERSION
    
@register.simple_tag    
def google_user():
    user = users.get_current_user()
    if user:
        return str(user.nickname())
    else:
        return "[a]"
    
@register.filter
def atom_date(value):
    if not value : return 'never'
    return value.strftime('%a %d %b %y')
    
@register.filter
def atom_priority(value):
    if not value or value>3 : return 'none'
    
    return int(value)
    
@register.filter
def atom_repeat_type(value):
    if not value: return 'none'
    
    return value
    
    