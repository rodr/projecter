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

class BaseTaskForm(forms.ModelForm):
    milestone = forms.ModelChoiceField(queryset=None, widget=forms.Select())

    def set_milestones(self, milestones):
        self.fields["milestone"].queryset = milestones

class TaskForm(BaseTaskForm):
    class Meta:
        model = Task
        exclude = ("changed_at",)

class TaskChangeForm(BaseTaskForm):
    comment = forms.CharField(required=True, widget=forms.Textarea())

    class Meta:
        model = Task
        exclude = ("description", "changed_at",)

##### Views

@login_required
def projects_index(request, template="templates/projects/index.html"):
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
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()

            messages.success(request, _("Project has been created."))

            return http.HttpResponseRedirect("/projects/")
    else:
        form = ProjectForm()

    return render_to_response(template, RequestContext(request, locals()))

@permission_required("project.change_project", login_url="/permission_required/")
def projects_edit(request, project_id, template="templates/projects/add.html"):
    project = get_object_or_404(Project, id=project_id)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()

            messages.success(request, _("Project has been succesfully edited."))

            return http.HttpResponseRedirect("/projects/%d/" % project.id)
    else:
        form = ProjectForm(instance=project)

    return render_to_response(template, RequestContext(request, locals()))

@login_required
def projects_project(request, project_id, template="templates/projects/project.html"):
    project = get_object_or_404(Project, id=project_id)
    milestones = Milestone.objects.filter(project=project)

    request_filter = request.GET.get("filter") 
    try:    
        request_target = int(request.GET.get("target"))
    except (TypeError, ValueError), err:
        request_target = 0
   
    filter_map = {
        "upcoming": Task.objects.filter(milestone__project=project).exclude(status="closed"),
        "closed": Task.objects.filter(milestone__project=project, status="closed"),
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
    milestone = get_object_or_404(Milestone, id=milestone_id)
    tasks_total = Task.objects.filter(milestone=milestone).count()
    tasks_completed = Task.objects.filter(milestone=milestone, status="closed").count()

    try: 
        graph_size = (float(tasks_completed)/float(tasks_total))*98
    except ZeroDivisionError, err:
        graph_size = -2

    return render_to_response(template, RequestContext(request, {
        "milestone": milestone,
        "tasks_total": int(tasks_total),
        "tasks_completed": int(tasks_completed),
        "graph_size": graph_size+2,
    }))

@permission_required("milestone.add_milestone", login_url="/permission_required/")
def projects_milestone_add(request, project_id, template="templates/projects/milestone_add.html"):
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
    task = get_object_or_404(Task, id=task_id)

    changes = TaskChange.objects.grouped(task)
    milestones = Milestone.objects.filter(project=task.milestone.project)

    if request.method == "POST":
        form = TaskChangeForm(request.POST, instance=task)
        form.set_milestones(milestones)

        if form.is_valid():
            _task = form.save(commit=False)
            _task.save(request, form.cleaned_data["comment"])

            messages.success(request, _("Task modified."))

            return http.HttpResponseRedirect("/tasks/%d/" % task.id)
    else:
        form = TaskChangeForm(instance=task)
        form.set_milestones(milestones)

    return render_to_response(template, RequestContext(request, {
        "task": task,
        "changes": changes,
        "form": form
    }))

@login_required
def projects_task_add(request, project_id, template="templates/projects/task_add.html"):
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
