from django.conf.urls import include, url

from .views import comments, discussions, groups, subscriptions


urlpatterns = [
    url(r'^$', groups.GroupList.as_view(), name='group-list'),
    url(r'^(?P<pk>\d+)/', include([
        url(
            r'^$',
            groups.GroupDetail.as_view(),
            name='group-detail',
        ),
        url(
            r'^new-discussion/$',
            discussions.DiscussionCreate.as_view(),
            name='discussion-create',
        ),
        url(
            r'^subscribe/$',
            subscriptions.GroupSubscribe.as_view(),
            name='group-subscribe',
        ),
    ])),
    url(r'^discussions/(?P<pk>\d+)/', include([
        url(
            r'^$',
            discussions.DiscussionThread.as_view(),
            name='discussion-thread',
        ),
        url(
            r'^post-with-attachment/$',
            comments.CommentPostWithAttachment.as_view(),
            name='comment-post-with-attachment',
        ),
        url(
            r'^subscribe/$',
            subscriptions.DiscussionSubscribe.as_view(),
            name='discussion-subscribe',
        ),
    ])),
    url(r'^comments/(?P<pk>\d+)/', include([
        url(
            r'^delete/$',
            comments.CommentDelete.as_view(),
            name='comment-delete',
        ),
    ])),
    url(
        r'^reply/',
        comments.CommentPostByEmail.as_view(),
        name='comment-reply',
    ),
]
