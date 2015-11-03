from django.conf.urls import include, url

from . import views


urlpatterns = [
    url(r'^$', views.GroupList.as_view(), name='group-list'),
    url(r'^(?P<pk>\d+)/', include([
        url(
            r'^$',
            views.GroupDetail.as_view(),
            name='group-detail',
        ),
        url(
            r'^new-discussion/$',
            views.DiscussionCreate.as_view(),
            name='discussion-create',
        ),
        url(
            r'^subscribe/$',
            views.GroupSubscribe.as_view(),
            name='group-subscribe',
        ),
    ])),
    url(r'^discussions/(?P<pk>\d+)/', include([
        url(
            r'^$',
            views.DiscussionThread.as_view(),
            name='discussion-thread',
        ),
        url(
            r'^subscribe/$',
            views.DiscussionSubscribe.as_view(),
            name='discussion-subscribe',
        ),
        url(
            r'^upload-file/$',
            views.CommentUploadFile.as_view(),
            name='comment-upload-file',
        ),
    ])),
    url(r'^comments/(?P<pk>\d+)/', include([
        url(
            r'^delete/$',
            views.CommentDelete.as_view(),
            name='comment-delete',
        ),
    ])),
    url(
        r'^reply/',
        views.CommentPostByEmail.as_view(),
        name='comment-reply',
    ),
]
