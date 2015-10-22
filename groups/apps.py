from django.apps import AppConfig


class GroupsConfig(AppConfig):
    """
    Configuration for `groups`.

    Provides:
    * default_within_days - a default parameter for the `within_days` methods on some
      of the model managers, which return items that were posted or posted to within
      that time period.
    """
    name = 'groups'
    default_within_days = 7

    new_comment_subject = 'New comment in {discussion}'
    new_discussion_subject = 'New discussion in {group}'
