import importlib

from django.apps import AppConfig
from django.contrib import admin


def get_class_from_path(class_path):
    """
    Retrieve a class from a Python path string.

    For example, get_class_from_path('users.models.User') would return the User class
    (which you can then instantiate, use for `instanceof` tests, and so on).
    """
    module_name, class_name = class_path.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


class AdminRegisteringAppConfig(AppConfig):
    """
    An AppConfig that will register ModelAdmins for you.

    Use this to allow library ModelAdmins to be customised easily in other projects,
    by providing paths to overridden ModelAdmin classes in the app config.

    To use AdminRegisteringAppConfig, subclass it instead of the normal AppConfig and
    fill in or append to the `admin_classes` attribute.  This is a dictionary of
    {<model_name>: <model_admin_class_path>}.

    class YourAppConfig(AdminRegisteringAppConfig):
        admin_classes = {
            'Group': 'an_app.admin.OverriddenGroupAdmin',
            'User': 'users.admin.MagicalUserAdmin',
        }

    AdminRegisteringAppConfig will do the rest.  It iterates over this dictionary and
    calls `admin.site.register` for each <model>:<admin> pair, *after* its normal
    setup process.  This means that admin classes registered in these AppConfigs will
    be registered after ones that are registered in `admin.py` files.

    If you want your admin class paths to be individual variables, for ease of future
    customisation, you can use update_admin_classes to implement this:

    class YourAppConfig(AdminRegisteringAppConfig):
        admin_classes = {}
        group_admin_class_path = 'an_app.admin.OverriddenGroupAdmin'
        user_admin_class_path = 'users.admin.MagicalUserAdmin'

        def update_admin_classes(self, admin_classes):
            super().update_admin_classes(admin_classes)
            admin_classes.update(**{
                'Group': self.group_admin_class_path,
                'User': self.user_admin_class_path,
            })

    This way, if your `AppConfig` is part of a library, a project using that library
    doesn't have to override the entirety of `admin_classes` in order to swap out
    one entry.
    """
    admin_classes = {}

    def update_admin_classes(self, admin_classes):
        """
        A hook method for any modifications to `admin_classes` that depend on other
        attributes of the AppConfig (which can be overridden by subclasses).
        """
        pass

    def _register_admin_classes(self):
        """Register each <model>:<admin_class> pair in self.admin_classes."""
        self.update_admin_classes(self.admin_classes)
        for model, admin_class in self.admin_classes.items():
            admin.site.register(
                self.get_model(model),
                get_class_from_path(admin_class)
            )

    def ready(self):
        """After performing normal Django setup, register our admin classes."""
        super(AdminRegisteringAppConfig, self).ready()
        self._register_admin_classes()
