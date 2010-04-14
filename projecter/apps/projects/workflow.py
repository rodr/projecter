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
    (1, _("request")),
    (2, _("bug")),
)

TASK_PRIORITY = (
    (1, _("urgent")),
    (2, _("high")),
    (3, _("normal")),
    (4, _("low")),
)

TASK_STATUS = (
    (1, _("new")),
    (2, _("research")),
    (3, _("process")),
    (4, _("review")),
    (5, _("accepted")),
    (6, _("resolved")),
    (7, _("closed")),
)
