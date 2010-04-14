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
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _

class EventType(models.Model):
    name = models.CharField(max_length=255)
    template = models.TextField()

    class Meta:
        db_table = "event_type"
    
class Event(models.Model):
    type = models.ForeignKey(EventType)
    user = models.ForeignKey(User, related_name="event_actor")
    recipients = models.ManyToManyField(User, related_name="event_recipients", through='EventRecipient')

    message = models.TextField()

    target_content_type = models.ForeignKey(ContentType, related_name="target", blank=True, null=True)
    target_object_id = models.PositiveIntegerField(blank=True, null=True)
    target = generic.GenericForeignKey('target_content_type', 'target_object_id')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "event"

class EventRecipient(models.Model):
    event = models.ForeignKey(Event)
    user = models.ForeignKey(User)
    public = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False, blank=True)

    class Meta:
        db_table = "event_recipients"

class SignalSettings(models.Model):
    user = models.ForeignKey(User)
    event_type = models.ForeignKey(EventType)
    medium = models.PositiveIntegerField(choices=((1, "email"),), default=1)
    send = models.BooleanField(default=True)

    class Meta:
        db_table = "signal_settings"
    
class Status(models.Model):
    user = models.ForeignKey(User)
    text = models.TextField()
    in_reply_to = models.ForeignKey("self")

    created_at = models.DateTimeField(auto_now_add=True)    

    class Meta:
        db_table = "status"
    
    def __unicode__(self):
        return u'%s' % self.text
