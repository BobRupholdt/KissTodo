from django.db import models

class List(models.Model):
    name = models.CharField(max_length=1000)

    def __unicode__(self):
        return u'%s' % (self.name)

    class Meta:
        ordering = ("name","id")
        
class Todo(models.Model):
    description = models.CharField(max_length=1000)
    priority= models.IntegerField(default=0)
    list = models.ForeignKey(List)

    def __unicode__(self):
        return u'%s' % (self.description)

    class Meta:
        ordering = ("description","id")        

        