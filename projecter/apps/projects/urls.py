from django.conf.urls.defaults import *

urlpatterns = patterns('projecter.apps.projects.views',
    (r'^projects/$', 'projects_index'),
    (r'^projects/add/$', 'projects_add'),
    (r'^projects/(?P<project_id>\d+)/$', 'projects_project'),
    (r'^projects/(?P<project_id>\d+)/edit/$', 'projects_edit'),
    (r'^projects/(?P<project_id>\d+)/add_task/$', 'projects_task_add'),
    (r'^projects/(?P<project_id>\d+)/add_milestone/$', 'projects_milestone_add'),
    (r'^tasks/(?P<task_id>\d+)/$', 'projects_task'),
    (r'^milestones/(?P<milestone_id>\d+)/$', 'projects_milestone'),
)
