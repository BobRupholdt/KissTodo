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

from django.test import TestCase
from datetime import date

from todo.models import *

class TodoTest(TestCase):
    def test_logic_and_phisical_delete(self):
        """
        Tests that Todo delete only put the deleted property to True, 
        without deleting the todo from the data store
        """
        
        l = List(name='myList', owner='me')
        l.save()
        
        t1=Todo(description='myTodo', list=l)
        t1.save()

        assert(len(l.todo_set.all())==1)
        assert(len(Todo.objects.all())==1)
        assert(len(Todo.objects_raw.all())==1)        
        
        t1.delete()
        
        assert(t1.deleted==True)
        
        assert(len(l.todo_set.all())==0)
        assert(len(Todo.objects.all())==0)
        assert(len(Todo.objects_raw.all())==1)                
        
        t1.delete_raw()        
        
        assert(len(l.todo_set.all())==0)
        assert(len(Todo.objects.all())==0)
        assert(len(Todo.objects_raw.all())==0)     

    def test_sorting(self):
        """
        Tests different todo sorting
        """
        
        l = List(name='myList', owner='me')
        l.save()
            
        t=Todo(description='t0', list=l, due_date=date(1999, 12, 31))
        t.save()
        
        t=Todo(description='t1', list=l, due_date=date(2030, 12, 31))
        t.save()   

        t=Todo(description='t2', list=l, due_date=date(2030, 12, 31), priority=1, complete=True)
        t.save() 

        t=Todo(description='t3', list=l, due_date=date(2030, 12, 31), priority=2)
        t.save()         
        
        t=Todo(description='t4', list=l, priority=3)
        t.save()            
        
        t=Todo(description='t5', list=l, due_date=date(1984, 12, 31))
        t.save()                    
    
        todos = Todo.todo_sort(Todo.objects.all(), 'D') # by date
        
        assert(todos[0].description=="t5")     
        assert(todos[1].description=="t0")     
        assert(todos[2].description=="t3")     
        assert(todos[3].description=="t1")     
        assert(todos[4].description=="t4")             
        assert(todos[5].description=="t2")      

        todos = Todo.todo_sort(Todo.objects.all(), 'P') # by priority

        assert(todos[0].description=="t3")     
        assert(todos[1].description=="t4")     
        assert(todos[2].description=="t5")     
        assert(todos[3].description=="t0")     
        assert(todos[4].description=="t1")             
        assert(todos[5].description=="t2")      
        
        todos = Todo.todo_sort(Todo.objects.all(), 'A') #  by description (a-z)

        assert(todos[0].description=="t0")     
        assert(todos[1].description=="t1")     
        assert(todos[2].description=="t3")     
        assert(todos[3].description=="t4")     
        assert(todos[4].description=="t5")             
        assert(todos[5].description=="t2")             
        
    def test_postpone(self):
        """
        Test postpone: if due_date is none, it is set to tomorrow, otherwise one more day is added
        """
        
        t=Todo()
        assert(t.due_date is None)
        t.postpone()
        d1=t.due_date
        assert(t.due_date == datetime.now().date() + timedelta(days=1))
        t.postpone()
        assert(t.due_date == d1 + timedelta(days=1))
  
class ListTest(TestCase):
    def test_logic_delete(self):
        """
        Tests that List.delete move the todo to the inbox list before 
        deleting the list itself
        """
        
        l = List(name='myList', owner='me')
        l.save()
        
        t1=Todo(description='myTodo', list=l)
        t1.save()

        assert(len(List.objects.all())==1)
        assert(List.objects.all()[0].name=="myList")
        
        l.delete()
        
        assert(len(List.objects.all())==1)
        assert(List.objects.all()[0].name==List.INBOX_LIST_NAME)
        assert(List.objects.all()[0].todo_set.all()[0].description=="myTodo")
        
    def test_raw_delete(self):
        """
        Tests raw delete: all todo are also deleted
        """
        
        l = List(name='myList', owner='me')
        l.save()
        
        t1=Todo(description='myTodo', list=l)
        t1.save()

        assert(len(List.objects.all())==1)
        assert(List.objects.all()[0].name=="myList")
        assert(len(Todo.objects_raw.all())==1)
        
        l.delete_raw()
        
        assert(len(List.objects.all())==0)
        assert(len(Todo.objects_raw.all())==0)
        


        
       
      
        
        
        


