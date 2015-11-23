from ._apps_base import AdminRegisteringAppConfig


class GroupsConfig(AdminRegisteringAppConfig):
    """
    Configuration for `groups`.

    Provides:
    * `default_within_days` - a default parameter for the `within_days` methods on some
      of the model managers, which return items that were posted or posted to within
      that time period.
    * `new_comment_subject` and `new_discussion_subject` - subjects for notification
      emails.  Each one will be formatted with the `{discussion}` a comment is on or the
      `{group}` a discussion belongs to, respectively.
    * `group_admin_class_path` and `discussion_admin_class_path` - these allow a project
      to override the admin behaviour of `incuna-groups`.
    """
    name = 'groups'

    default_within_days = 7

    new_comment_subject = 'New comment on {discussion}'
    new_discussion_subject = 'New discussion in {group}'

    group_admin_class_path = 'groups.admin.GroupAdmin'
    discussion_admin_class_path = 'groups.admin.DiscussionAdmin'

    admin_classes = {
        'Group': group_admin_class_path,
        'Discussion': discussion_admin_class_path,
    }
