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
    ])),
]
