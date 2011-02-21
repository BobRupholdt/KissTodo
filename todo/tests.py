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
        
        l.delete("me")
        
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
        


        
       
      
        
        
        


