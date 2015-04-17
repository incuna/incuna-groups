from django.apps import apps as django_apps
from django.test import TestCase


class TestGroupsConfig(TestCase):
    config = django_apps.get_app_config('groups')

    def test_default_active_threshold_days(self):
        """Assert this member exists and has the right value."""
        value = self.config.default_active_threshold_days
        self.assertEqual(value, 7)
