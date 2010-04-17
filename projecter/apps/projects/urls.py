from django.conf.urls.defaults import *

urlpatterns = patterns('projecter.apps.projects.views',
    (r'^projects/$', 'projects_index'),
    (r'^projects/(?P<project_id>\d+)/$', 'projects_project'),
    (r'^tasks/(?P<task_id>\d+)/$', 'projects_task'),
)
