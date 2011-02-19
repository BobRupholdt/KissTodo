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

from django.db import models

class List(models.Model):
    name = models.CharField(max_length=1000)
    owner = models.CharField(max_length=255)

    def __unicode__(self):
        return u'%s' % (self.name)

    class Meta:
        ordering = ("name","id")
        
class TodoManager(models.Manager):
    def get_query_set(self):
        return super(TodoManager, self).get_query_set().filter(deleted=False)
        
class Todo(models.Model):
    description = models.CharField(max_length=1000)
    priority = models.IntegerField(default=4)
    complete = models.BooleanField(default=False)
    list = models.ForeignKey(List)
    
    deleted = models.BooleanField(default=False)
    
    objects = TodoManager() 
    
    def delete(self): 
        self.deleted=True
        self.save()
            
    def __unicode__(self):
        return u'%s' % (self.description)

    class Meta:
        ordering = ("complete","priority","description","id")        

        