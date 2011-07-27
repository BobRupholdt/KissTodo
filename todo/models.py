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
from django.db.models import Q
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

class ListManager(models.Manager):
    
    def get_or_create_inbox(self, user):
        inbox, created = self.get_or_create(name=List.INBOX_LIST_NAME, owner=user)
        return inbox

class List(models.Model):

    INBOX_LIST_NAME = '@inbox'
    HOT_LIST_NAME = '@hot'
    ALL_LIST_NAME = '@all'
    TRASH_LIST_NAME = '@trash'
    
    name = models.CharField(max_length=5000)
    owner = models.CharField(max_length=255)
    
    objects = ListManager() 
    
    def is_special(self):
        return self.name==List.INBOX_LIST_NAME or self.name==List.HOT_LIST_NAME or self.name==List.TRASH_LIST_NAME

    def __unicode__(self):
        return u'%s' % (self.name)
        
    def delete(self): 
        if self.name==List.INBOX_LIST_NAME: return
        if self.name==List.HOT_LIST_NAME: return
        if self.name==List.TRASH_LIST_NAME: return
        if self.name==List.ALL_LIST_NAME: return
        
        todos_raw = Todo.objects_raw.filter(list=self).all()
        
        if len(todos_raw)>0:
            inbox_list = List.objects.get_or_create_inbox(self.owner)
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
        
    def hot(self, user):
        
        next_days = datetime.now()+timedelta(days=7)
        
        todos_with_priority = Q(complete=False, priority__lt=4)
        todo_within_next_days = Q(complete=False, due_date__lte=next_days, due_date__isnull=False)
        
        hot = list(self.filter(todos_with_priority).order_by("priority", "description"))
        
        # GAE does not supports OR query
        for t in self.filter(todo_within_next_days).order_by("due_date", "description"):
            if not t in hot: hot.append(t)
        
        #hot = self.filter(complete=False, priority__lt=4).order_by("priority", "description")
        
        #due to a GAE limitation, it is not possibile to filter on list__owner
        return [t for t in hot if t.list.owner == user]
        
    def deleted(self, user):
        deleted = super(TodoManager, self).get_query_set().filter(deleted=True).order_by("priority", "description")
        
        #due to a GAE limitation, it is not possibile to filter on list__owner
        return [t for t in deleted if t.list.owner == user]   

    def all_by_user(self, user):
        return [t for t in self.all() if t.list.owner == user]

class Todo(models.Model):
    description = models.CharField(max_length=5000)
    priority = models.IntegerField(default=4)
    complete = models.BooleanField(default=False)
    list = models.ForeignKey(List)
    deleted = models.BooleanField(default=False)
    due_date = models.DateTimeField(null=True, blank=True)
    
    repeat_type_choiches = (('', ' - no repeat - '),    ('d', 'days'),    ('w', 'weeks'),   ('m', 'months'), ('y', 'years'),)
    
    repeat_type = models.CharField(max_length=1, choices=repeat_type_choiches, null=True, blank=True)
    repeat_every = models.IntegerField(null=True, blank=True)
    
    external_source = models.CharField(max_length=255, blank=True)
    external_id = models.CharField(null=True,max_length=2000)    
    
    objects = TodoManager() 
    objects_raw = models.Manager() 
    
    def delete(self): 
        if self.deleted==False:
            self.deleted=True
            self.save()
        else:
            self.delete_raw()
            
    def toggle_complete(self): 
         if self.complete:
            self.complete = False
         else:
            if (self.repeat_type and self.repeat_every):
            
                today = datetime.now().date()
                
                if self.repeat_type=="d":
                    self.due_date = today + timedelta(days=self.repeat_every)
                elif self.repeat_type=="w":
                    self.due_date = today + timedelta(days=self.repeat_every*7)
                elif self.repeat_type=="m":
                    self.due_date = today + relativedelta(months=self.repeat_every)
                elif self.repeat_type=="y":
                    self.due_date = today + relativedelta(years=self.repeat_every)
            else:
                self.complete = True
        
    def undelete(self): 
        self.deleted=False
        self.save()        
        
    def delete_raw(self): 
        super(Todo, self).delete()

    def is_today(self): 
        if self.due_date is None: return False
        return self.due_date.date() == datetime.now().date()        
        
    def is_overdue(self): 
        if self.due_date is None: return False
        return self.due_date.date() < datetime.now().date()
        
    def postpone(self): 
        if self.due_date is None: self.due_date = datetime.now().date()
        self.due_date = self.due_date + timedelta(days=1)
            
    def __unicode__(self):
        return u'%s' % (self.description)

    class Meta:
        ordering = ("complete","due_date","priority","description","id")        

    @staticmethod
    def todo_sort(todos, mode):
        if mode=='D':
            todos=list(todos)
            todos.sort(Todo._todo_sort_date)
        elif mode=='P':
            todos=list(todos)
            todos.sort(Todo._todo_sort_priority)      
        elif mode=='A':
            todos=list(todos)
            todos.sort(Todo._todo_sort_az)                  
        else:
            raise Exception("Unknown sort mode: "+mode)
        return todos
    
    @staticmethod    
    def _todo_sort_date(t1, t2):
        if t1.complete!=t2.complete:
            if t1.complete: return 1
            return -1
        elif t1.due_date!=t2.due_date:
            if t1.due_date==None: return 1
            if t2.due_date==None: return -1
            if t1.due_date<t2.due_date: return -1
            return 1
        elif t1.priority!=t2.priority:
            if t1.priority<t2.priority: return -1
            return 1   
        elif t1.description!=t2.description:
            if t1.description<t2.description: return -1
            return 1   
        elif t1.id!=t2.id:
            if t1.id<t2.id: return -1
            return 1               
        else:
            return 0
            
    @staticmethod    
    def _todo_sort_priority(t1, t2):
        if t1.complete!=t2.complete:
            if t1.complete: return 1
            return -1
        elif t1.priority!=t2.priority:
            if t1.priority<t2.priority: return -1
            return 1 
        elif t1.due_date!=t2.due_date:
            if t1.due_date==None: return 1
            if t2.due_date==None: return -1
            if t1.due_date<t2.due_date: return -1
            return 1                
        elif t1.description!=t2.description:
            if t1.description<t2.description: return -1
            return 1   
        elif t1.id!=t2.id:
            if t1.id<t2.id: return -1
            return 1               
        else:
            return 0            
            
    @staticmethod    
    def _todo_sort_az(t1, t2):
        if t1.complete!=t2.complete:
            if t1.complete: return 1
            return -1
        elif t1.description!=t2.description:
            if t1.description<t2.description: return -1
            return 1              
        elif t1.priority!=t2.priority:
            if t1.priority<t2.priority: return -1
            return 1 
        elif t1.due_date!=t2.due_date:
            if t1.due_date==None: return 1
            if t2.due_date==None: return -1
            if t1.due_date<t2.due_date: return -1
            return 1                
        elif t1.id!=t2.id:
            if t1.id<t2.id: return -1
            return 1               
        else:
            return 0            

                    