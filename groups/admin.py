from django.contrib import admin

from .models import Discussion, Group


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('moderators', 'members_if_private')
    exclude = ('watchers',)

    class Meta:
        model = Group


@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    exclude = ('subscribers', 'ignorers')

    class Meta:
        model = Discussion
