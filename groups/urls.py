from django.conf.urls import include, url

from . import views


urlpatterns = [
    url(r'^$', views.groups.GroupList.as_view(), name='group-list'),
    url(r'^(?P<pk>\d+)/', include([
        url(
            r'^$',
            views.groups.GroupDetail.as_view(),
            name='group-detail',
        ),
        url(
            r'^new-discussion/$',
            views.discussions.DiscussionCreate.as_view(),
            name='discussion-create',
        ),
        url(
            r'^subscribe/$',
            views.subscriptions.GroupSubscribe.as_view(),
            name='group-subscribe',
        ),
    ])),
    url(r'^discussions/(?P<pk>\d+)/', include([
        url(
            r'^$',
            views.discussions.DiscussionThread.as_view(),
            name='discussion-thread',
        ),
        url(
            r'^upload-file/$',
            views.comments.CommentUploadFile.as_view(),
            name='comment-upload-file',
        ),
        url(
            r'^subscribe/$',
            views.subscriptions.DiscussionSubscribe.as_view(),
            name='discussion-subscribe',
        ),
    ])),
    url(r'^comments/(?P<pk>\d+)/', include([
        url(
            r'^delete/$',
            views.comments.CommentDelete.as_view(),
            name='comment-delete',
        ),
    ])),
    url(
        r'^reply/',
        views.comments.CommentPostByEmail.as_view(),
        name='comment-reply',
    ),
]
