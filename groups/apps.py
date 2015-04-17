from django.apps import AppConfig


class GroupsConfig(AppConfig):
    """
    Configuration for `groups`.

    Provides:
    * default_active_threshold_days - a user is considered not to be active if they
      haven't made a comment within the past [this value] days, and vice versa.  A
      discussion or group is considered to be active if it has at least one active user.
      This setting is a default, used only when a value isn't supplied manually to the
      various methods that return active things.
    """
    name = 'groups'
    default_active_threshold_days = 7
