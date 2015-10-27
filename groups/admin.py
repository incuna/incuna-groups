from django.contrib import admin

from .models import Discussion, Group


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('moderators', 'watchers', 'members_if_private')

    class Meta:
        model = Group


@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    filter_horizontal = ('subscribers', 'ignorers')

    class Meta:
        model = Discussion
