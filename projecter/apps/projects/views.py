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
from django.views.decorators.cache import cache_page

from projecter.apps.projects.models import Project, Milestone, Task, TaskChange

@cache_page(60*60)
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

def projects_project(request, project_id, template="templates/projects/project.html"):
    project = get_object_or_404(Project, id=project_id)
    milestones = Milestone.objects.filter(project=project)

    request_filter = request.GET.get("filter") 
    try:    
        request_target = int(request.GET.get("target"))
    except (TypeError, ValueError):
        request_target = 0
   
    filter_map = {
        "upcoming": Task.objects.filter(milestone__project=project).exclude(status=7),
        "closed": Task.objects.filter(milestone__project=project, status=7),
        #"assigned_to_me": Task.objects.filter(milestone__project=project, users=request.user),
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

def projects_task(request, task_id, template="templates/projects/task.html"):
    task = get_object_or_404(Task, id=task_id)
    changes = TaskChange.objects.for_task(task)
    return render_to_response(template, RequestContext(request, {
        "task": task,
        "changes": changes
    }))

def projects_milestone(request, milestone_id, template="templates/projects/milestone.html"):
    milestone = get_object_or_404(Milestone, id=milestone_id)
    tasks_total = Task.objects.filter(milestone=milestone).count() #TODO: use char for this
    tasks_completed = Task.objects.filter(milestone=milestone, status=7).count()

    graph_size = (tasks_completed/tasks_total)*98

    tasks = Task.objects.by_changes()

    return render_to_response(template, RequestContext(request, {
        "milestone": milestone,
        "tasks_total": tasks_total,
        "tasks_completed": tasks_completed,
        "graph_size": graph_size+2,
        "tasks": tasks
    }))