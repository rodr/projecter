from django.conf.urls.defaults import *

urlpatterns = patterns('projecter.apps.accounts.views',
    (r'^login/$', 'accounts_login'),
    (r'^logout/$', 'accounts_logout'),
    (r'^permission_required/$', 'accounts_permission_required'),
    (r'^user/(?P<username>\w+)/$', 'accounts_profile'),
)
