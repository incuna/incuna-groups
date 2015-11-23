from django.contrib import admin


# Registered in the `AppConfig`
class GroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('moderators', 'members_if_private')
    exclude = ('watchers',)


# Also registered in the `AppConfig`
class DiscussionAdmin(admin.ModelAdmin):
    exclude = ('subscribers', 'ignorers')
