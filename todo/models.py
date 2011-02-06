from django.db import models

class TodoList(models.Model):
    name = models.CharField(max_length=1000)

    def __unicode__(self):
        return u'%s' % (self.name)

    class Meta:
        ordering = ("name","id")

        
