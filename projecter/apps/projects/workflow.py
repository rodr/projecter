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

from django.utils.translation import ugettext as _


TASK_TYPE = (
    ("request", _("Request")),
    ("bug", _("Bug")),
)

TASK_PRIORITY = (
    ("urgent", _("Urgent")),
    ("high", _("High")),
    ("normal", _("Normal")),
    ("low", _("Low")),
)

TASK_STATUS = (
    ("new", _("New")),
    ("research", _("Research")),
    ("process", _("Process")),
    ("review", _("Review")),
    ("accepted", _("Accepted")),
    ("resolved", _("Resolved")),
    ("closed", _("Closed")),
)
