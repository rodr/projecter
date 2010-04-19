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

import logging
import time

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.forms.models import model_to_dict

from projecter.apps.accounts.models import Company
from projecter.apps.projects import workflow

##### Managers

class TaskManager(models.Manager):
    pass

class TaskChangeManager(models.Manager):
    def for_task(self, task):
        changes = self.filter(task=task).all()

        return changes

    def grouped(self, task):
        changes = self.for_task(task)
        num = 0
        last_uid = None
        for change in changes:
            uid = (change.created_at, change.user)
            if uid != last_uid:
                current = {
                    "user": change.user,
                    "created_at": change.created_at,
                    "fields":[],
                    "num": num
                }
                num += 1
                last_uid = uid

                yield current

            if change.field == "comment":
                current["comment"] = change.new_value
            else:
                current["fields"].append({
                    "label": change.field,                    
                    "old": change.old_value,
                    "new": change.new_value
                })

##### Models

class Project(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    company = models.ForeignKey(Company)

    managers = models.ManyToManyField(User, related_name="project_managers")
    people = models.ManyToManyField(User, related_name="project_people")

    class Meta:
        db_table = "project"
        ordering = ["name"]
    
    def __unicode__(self):
        return u"%s" % self.name

    @models.permalink
    def get_absolute_url(self):
        return ('project_detail', {"id": self.id})

class Milestone(models.Model):
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=255)
    description = models.TextField()
  
    class Meta:
        db_table = "milestone"

    def __unicode__(self):
        return u"%s" % self.name

    @models.permalink
    def get_absolute_url(self):
        return ('milestone_detail', {"id": self.id})

class Task(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    users = models.ManyToManyField(User)

    type = models.CharField(max_length=100, choices=workflow.TASK_TYPE)
    priority = models.CharField(max_length=100, choices=workflow.TASK_PRIORITY)
    status = models.CharField(max_length=100, choices=workflow.TASK_STATUS)

    milestone = models.ForeignKey(Milestone)

    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now_add=True, auto_now=True)

    duration = models.IntegerField(default=1)

    objects = TaskManager()

    class Meta:
        db_table = "task"
        ordering = ["-created_at", "priority", "status"]

    def __init__(self, *args, **kwargs):
        super(Task, self).__init__(*args, **kwargs)

        self._old = {
            "name": self.name,
            "status": self.status,
            "comment": None,
            "priority": self.priority,
            "duration": self.duration,
            "type": self.type
        }

    def __unicode__(self):
        return u"%s" % self.name

    @models.permalink
    def get_absolute_url(self):
        return ('task_detail', {"id": self.id})

    def save(self, request=None, comment=None):
        if self._old and request:
            new = model_to_dict(self)
            new["comment"] = comment

            _version = time.time()

            for field in self._old.keys():
                if self._old[field] != new[field]:            
                    change = {
                        "user": request.user,
                        "task": self,
                        "field": field,
                        "old_value": self._old[field],
                        "new_value": new[field],
                        "created_at": _version
                    }
                    TaskChange(**change).save()

        super(Task, self).save()

class TaskChange(models.Model):
    _TASK_FIELDS = (
        ("status", _("Status")),
        ("comment", _("Comment")),
        ("priority", _("Priority")),
        ("duration", _("Duration")),
        ("type", _("Type")),
        ("name", _("Name")),
    )

    user = models.ForeignKey(User)
    task = models.ForeignKey(Task)
    created_at = models.DateTimeField(auto_now_add=True)

    field = models.CharField(max_length=100, choices=_TASK_FIELDS)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)

    objects = TaskChangeManager()

    class Meta:
        db_table = "task_change"

    def __unicode__(self):
        return u"%s" % self.field
