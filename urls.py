from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

from django.conf import settings
urlpatterns = patterns('',

    
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),   
    
    (r'^todo/', include('todo.urls')),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT}),
)
