# Copyright 2010 Podcaster SA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

class Company(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return u'%s' % self.name
    
    class Meta:
        db_table = "company"
        verbose_name_plural = _("companies")
        
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    company = models.ForeignKey(Company)
    title = models.CharField(max_length=255)

    setup_done = models.BooleanField(default=False)
    
    class Meta:
        db_table = "user_profile"
