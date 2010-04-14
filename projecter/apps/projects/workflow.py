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
