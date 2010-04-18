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

from django import http
from django.conf import settings
from django.template import RequestContext

from django.shortcuts import render_to_response, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.cache import cache_page
from django.utils.translation import ugettext as _
from django import forms

from projecter.apps.projects.models import Project, Milestone, Task, TaskChange

##### Forms

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project

class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        exclude = ("project",)

class TaskForm(forms.ModelForm):
    milestone = forms.ModelChoiceField(queryset=None, widget=forms.Select())

    class Meta:
        model = Task

    def set_milestones(self, milestones):
        self.fields["milestone"].queryset = milestones

##### Views

@login_required
def projects_index(request, template="templates/projects/index.html"):
    """Shows all projects in a list, is orderable by name and company."""

    order_map = {
        "name": "name",
        "company": "company"
    }
    request_order = request.GET.get("order", "name")    
    if request_order in order_map:
        projects = Project.objects.order_by(order_map[request_order])
    else:
        projects = Project.objects.all()

    return render_to_response(template, RequestContext(request, {
        "projects": projects
    }))

@permission_required("project.add_project", login_url="/permission_required/")
def projects_add(request, template="templates/projects/add.html"):
    """The form for adding a project."""

    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()

            messages.success(request, _("The project has been created."))

            return http.HttpResponseRedirect("/projects/")
    else:
        form = ProjectForm()

    return render_to_response(template, RequestContext(request, locals()))

@permission_required("project.change_project", login_url="/permission_required/")
def projects_edit(request, project_id, template="templates/projects/add.html"):
    """Edit a project given a valid project_id."""

    project = get_object_or_404(Project, id=project_id)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()

            messages.success(request, _("The project has been succesfully edited."))

            return http.HttpResponseRedirect("/projects/%d/" % project.id)
    else:
        form = ProjectForm(instance=project)

    return render_to_response(template, RequestContext(request, locals()))

@login_required
def projects_project(request, project_id, template="templates/projects/project.html"):
    """The project dashboard. Shows all its tasks and milestones."""

    project = get_object_or_404(Project, id=project_id)
    milestones = Milestone.objects.filter(project=project)

    request_filter = request.GET.get("filter") 
    try:    
        request_target = int(request.GET.get("target"))
    except (TypeError, ValueError), err:
        request_target = 0
   
    filter_map = {
        "upcoming": Task.objects.filter(milestone__project=project).exclude(status=7),
        "closed": Task.objects.filter(milestone__project=project, status=7),
        "assigned_to_me": Task.objects.filter(milestone__project=project, users=request.user),
        "assigned_to": Task.objects.filter(milestone__project=project, users__id=request_target),
        "by_milestone": Task.objects.filter(milestone__project=project, milestone__id=request_target)
    }

    if request_filter in filter_map:
        tasks = filter_map[request_filter]
    else:
        tasks = Task.objects.filter(milestone__project=project)

    return render_to_response(template, RequestContext(request, {
        "project": project,
        "milestones": milestones,
        "tasks": tasks
    }))

@login_required
def projects_milestone(request, milestone_id, template="templates/projects/milestone.html"):
    """An overview of a milestone given its id."""

    milestone = get_object_or_404(Milestone, id=milestone_id)
    tasks_total = float(Task.objects.filter(milestone=milestone).count()) #TODO: fix numeration!
    tasks_completed = float(Task.objects.filter(milestone=milestone, status=7).count()) #TODO: use TaskStatus
    try: 
        graph_size = (tasks_completed/tasks_total)*98.0
    except ZeroDivisionError, err:
        graph_size = -2

    tasks = Task.objects.by_changes(milestone)

    return render_to_response(template, RequestContext(request, {
        "milestone": milestone,
        "tasks_total": int(tasks_total),
        "tasks_completed": int(tasks_completed),
        "graph_size": graph_size+2,
        "tasks": tasks
    }))

def projects_milestone_add(request, project_id, template="templates/projects/milestone_add.html"):
    """Form for adding a milestone to a project given its id."""
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == "POST":
        form = MilestoneForm(request.POST)
        if form.is_valid():
            _form = form.save(commit=False)
            _form.project = project
            _form.save()

            messages.success(request, _("Milestone added."))

            return http.HttpResponseRedirect("/projects/%d/" % project.id)
    else:
        form = MilestoneForm()
  
    return render_to_response(template, RequestContext(request, {
        "form": form
    }))

@login_required
def projects_task(request, task_id, template="templates/projects/task.html"):
    """Detail of a task including its changes."""
    task = get_object_or_404(Task, id=task_id)

    changes = TaskChange.objects.for_task(task)
    milestones = Milestone.objects.filter(project=task.milestone.project)

    from django.forms.models import model_to_dict
    _task = model_to_dict(task, fields=["status", "description", "priority", "duration", "type", "name"])
    
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        form.set_milestones(milestones)

        if form.is_valid():
            import time
            version_time = time.time()
            logging.debug("Saving change of task at <%d>" % version_time)

            for _key in _task.keys():
                logging.debug("%s: from \"%s\" to \"%s\"" % (_key, _task[_key], form.cleaned_data[_key]))
                if _task[_key] != form.cleaned_data[_key]:
                    field_revision = TaskChange()
                    field_revision.user = request.user
                    field_revision.task = task

                    field_revision.field = _key
                    field_revision.old_value = _task[_key]
                    field_revision.new_value = form.cleaned_data[_key]

                    field_revision.created_at = version_time
                    field_revision.save()

            form.save()
            messages.success(request, "Task modified.")

            return http.HttpResponseRedirect("/tasks/%d/" % task.id)
    else:
        form = TaskForm(instance=task)
        form.set_milestones(milestones)
    return render_to_response(template, RequestContext(request, {
        "task": task,
        "changes": changes,
        "form": form
    }))

@login_required
def projects_task_add(request, project_id, template="templates/projects/task_add.html"):
    """Form for adding a task to a project given its id."""

    project = get_object_or_404(Project, id=project_id)
    milestones = Milestone.objects.filter(project=project)

    if request.method == "POST":
        form = TaskForm(request.POST)
        form.set_milestones(milestones.all())

        if form.is_valid():
            form.save()

            messages.success(request, _("Task added."))

            return http.HttpResponseRedirect("/projects/%d/" % project.id)
    else:
        form = TaskForm()
        form.set_milestones(milestones)    

    return render_to_response(template, RequestContext(request, {
        "form": form
    }))   
