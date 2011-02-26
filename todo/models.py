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

    INBOX_LIST_NAME = '@inbox'
    HOT_LIST_NAME = '@hot'
    TRASH_LIST_NAME = '@trash'
    
    name = models.CharField(max_length=1000)
    owner = models.CharField(max_length=255)

    def __unicode__(self):
        return u'%s' % (self.name)
        
    def delete(self): 
        if self.name==List.INBOX_LIST_NAME: return
        if self.name==List.HOT_LIST_NAME: return
        if self.name==List.TRASH_LIST_NAME: return
        
        todos_raw = Todo.objects_raw.filter(list=self).all()
        if len(todos_raw)>0:
            inbox_list, created = List.objects.get_or_create(owner=self.owner, name=List.INBOX_LIST_NAME)
            for t in todos_raw: 
                t.list=inbox_list
                t.save()
        
        self.delete_raw()    
        
    def delete_raw(self):
        for t in Todo.objects_raw.filter(list=self).all(): t.delete_raw() # required by google app engine due to the lack of cascade delete
        super(List, self).delete()

    class Meta:
        ordering = ("name","id")
        
class TodoManager(models.Manager):
    def get_query_set(self):
        return super(TodoManager, self).get_query_set().filter(deleted=False)
        
    def hot(self, current_user):
        hot = self.get_query_set().filter(complete=False, priority__lt=4).order_by("priority", "description")
        
        #due to a GAE limitation, it is not possibile to filter on list__owner
        return [t for t in hot if t.list.owner == current_user]
        
    def deleted(self, current_user):
        deleted = super(TodoManager, self).get_query_set().filter(deleted=True).order_by("priority", "description")
        
        #due to a GAE limitation, it is not possibile to filter on list__owner
        return [t for t in deleted if t.list.owner == current_user]        
        
class Todo(models.Model):
    description = models.CharField(max_length=1000)
    priority = models.IntegerField(default=4)
    complete = models.BooleanField(default=False)
    list = models.ForeignKey(List)
    deleted = models.BooleanField(default=False)
    
    objects = TodoManager() 
    objects_raw = models.Manager() 
    
    def delete(self): 
        if self.deleted==False:
            self.deleted=True
            self.save()
        else:
            self.delete_raw()
        
    def undelete(self): 
        self.deleted=False
        self.save()        
        
    def delete_raw(self): 
        super(Todo, self).delete()
            
    def __unicode__(self):
        return u'%s' % (self.description)

    class Meta:
        ordering = ("complete","priority","description","id")        

        