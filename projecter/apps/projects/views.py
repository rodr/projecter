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

from django import http
from django.conf import settings
from django.template import RequestContext

from django.shortcuts import render_to_response, get_object_or_404
from django.contrib import messages
from django.views.decorators.cache import cache_page

from projecter.apps.projects.models import Project, Milestone, Task, TaskChange

@cache_page(60*60)
def projects_index(request, template="templates/projects/index.html"):
    projects = Project.objects.all()

    return render_to_response(template, RequestContext(request, {
        "projects": projects
    }))

def projects_project(request, project_id, template="templates/projects/project.html"):
    project = get_object_or_404(Project, id=project_id)
    milestones = Milestone.objects.filter(project=project)
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
