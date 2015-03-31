from django.db import models


class ChainedQuerySetManager(models.Manager):
    """
    Generic manager for querysets that need chainable methods.

    This does the same thing as django 1.7's QuerySet.as_manager() for a wider variety
    of Django versions.

    A subclass requires a queryset_class attribute.
    """
    def __getattr__(self, name):
        """Pass any called methods onto the queryset to make use of its chaining."""
        return getattr(self.get_queryset(), name)

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)
