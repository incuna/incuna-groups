from django.contrib import admin


class GroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('moderators', 'members_if_private')
    exclude = ('watchers',)


class DiscussionAdmin(admin.ModelAdmin):
    exclude = ('subscribers', 'ignorers')
