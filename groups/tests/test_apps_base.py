try:
    from unittest import mock
except ImportError:
    import mock

from django.test import TestCase

import groups  # Needed for instantiating AppConfig classes.
from groups import _apps_base
from groups.admin import GroupAdmin
from groups.models import Group


class TestAdminRegisteringAppConfig(TestCase):
    def setUp(self):
        """
        Create an AdminRegisteringAppConfig pointed at whichever models we have handy.
        """
        self.config = _apps_base.AdminRegisteringAppConfig('groups', groups)

    def test_register_admin_classes(self):
        """
        Assert that admin.site.register() is called based on the value of admin_classes,
        and update_admin_classes() is also called (although it does nothing).
        """
        self.config.admin_classes = {
            'Group': 'groups.admin.GroupAdmin',
        }

        # Mock out get_model() because otherwise the AppConfig will try to check if it's
        # prepared the models already, which it hasn't since we're shortcutting the
        # process to get a better unit test.  Assert that it's called with the correct
        # input later on to make sure we're not cheating.
        with mock.patch.object(self.config, 'get_model', return_value=Group) as get_model:
            with mock.patch.object(self.config, 'update_admin_classes') as update_admin:
                with mock.patch('django.contrib.admin.site.register') as site_register:
                    self.config._register_admin_classes()

        update_admin.assert_called_once_with(self.config.admin_classes)
        get_model.assert_called_once_with('Group')
        site_register.assert_called_once_with(Group, GroupAdmin)

    def test_ready(self):
        """
        Assert that ready() calls _register_admin_classes() and the superclass's ready().
        """
        with mock.patch('django.apps.config.AppConfig.ready') as super_ready:
            with mock.patch.object(self.config, '_register_admin_classes') as register:
                self.config.ready()

        super_ready.assert_called_once_with()
        register.assert_called_once_with()
