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

from projecter.apps.accounts.models import Company
from projecter.apps.projects import workflow

class TaskManager(models.Manager):
    pass

class TaskChangeManager(models.Manager):
    def for_task(self, task):
        changes = self.filter(task=task).all()

        return changes

class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    company = models.ForeignKey(Company)

    managers = models.ManyToManyField(User, related_name="project_managers")
    people = models.ManyToManyField(User, related_name="project_people")

    class Meta:
        db_table = "project"
    
    def __unicode__(self):
        return u"%s" % self.name

class Milestone(models.Model):
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=255)
    description = models.TextField()
  
    class Meta:
        db_table = "milestone"

    def __unicode__(self):
        return u"%s" % self.name

class Task(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    users = models.ManyToManyField(User)

    type = models.PositiveIntegerField(choices=workflow.TASK_TYPE, default=10)
    priority = models.PositiveIntegerField(choices=workflow.TASK_PRIORITY, default=30)
    status = models.PositiveIntegerField(choices=workflow.TASK_STATUS, default=30)

    milestone = models.ForeignKey(Milestone)

    created_at = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(default=1)

    objects = TaskManager()

    class Meta:
        db_table = "task"
        ordering = ["-created_at", "priority"]

    def __unicode__(self):
        return u"%s" % self.name

    @models.permalink
    def get_absolute_url(self):
        return ('task_detail', {"id": self.id})

class TaskNudge(models.Model):
    user = models.ForeignKey(User)
    task = models.ForeignKey(Task)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "task_nudge"

class TaskChange(models.Model):
    TASK_FIELDS = ( #TODO: workaround this kind of events
        (1, "name"),
        (2, "description"),
        (3, "users"),
        (4, "type"),
        (5, "priority"),
        (6, "status"),
        (7, "milestone"),
        (8, "duration"),
    )

    user = models.ForeignKey(User)
    task = models.ForeignKey(Task)
    comment = models.TextField(blank=True)

    field = models.PositiveIntegerField(choices=TASK_FIELDS, default=1)
    old_value = models.TextField()
    new_value = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    objects = TaskChangeManager()

    class Meta:
        db_table = "task_change"

#TODO models.signals.post_save.connect(new_task, sender=Task)
#TODO models.signals.post_save.connect(user_nudge_task, sender=TaskNudge)
#TODO models.signals.post_save.connect(new_task_change, sender=TaskChange)
