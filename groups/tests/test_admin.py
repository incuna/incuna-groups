from incuna_test_utils.testcases.integration import BaseAdminIntegrationTestCase

from . import factories
from .. import models


class AdminTestCase(BaseAdminIntegrationTestCase):
    user_factory = factories.AdminFactory


class GroupAdminTestCase(AdminTestCase):
    model = models.Group


class DiscussionAdminTestCase(AdminTestCase):
    model = models.Discussion


class TestGroupAdminChangelist(GroupAdminTestCase):
    def test_changelist(self):
        response = self.get_admin_changelist_page()
        self.assertEqual(response.status_code, 200)


class TestGroupAdminChange(GroupAdminTestCase):
    def test_change(self):
        obj = factories.GroupFactory.create()
        response = self.get_admin_change_page(obj)
        self.assertEqual(response.status_code, 200)


class TestGroupAdminDelete(GroupAdminTestCase):
    def test_delete(self):
        obj = factories.GroupFactory.create()
        response = self.get_admin_delete_page(obj)
        self.assertEqual(response.status_code, 200)


class TestDiscussionAdminChangelist(DiscussionAdminTestCase):
    def test_changelist(self):
        response = self.get_admin_changelist_page()
        self.assertEqual(response.status_code, 200)


class TestDiscussionAdminChange(DiscussionAdminTestCase):
    def test_change(self):
        obj = factories.DiscussionFactory.create()
        response = self.get_admin_change_page(obj)
        self.assertEqual(response.status_code, 200)


class TestDiscussionAdminDelete(DiscussionAdminTestCase):
    def test_delete(self):
        obj = factories.DiscussionFactory.create()
        response = self.get_admin_delete_page(obj)
        self.assertEqual(response.status_code, 200)
