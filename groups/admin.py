from django.contrib import admin

from .models import Discussion, Group


class GroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('moderators', 'watchers', 'members_if_private')

    class Meta:
        model = Group


class DiscussionAdmin(admin.ModelAdmin):
    filter_horizontal = ('subscribers', 'ignorers')

    class Meta:
        model = Discussion


admin.site.register(Group, GroupAdmin)
admin.site.register(Discussion, DiscussionAdmin)
