from django.apps import apps
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect
from django.views.generic import CreateView
from incuna_mail import send

from .. import models

NEW_COMMENT_SUBJECT = apps.get_app_config('groups').new_comment_subject


def get_reply_address(discussion, user, request):
    """
    Wrap a discussion reply UUID in an email address suitable for use as a reply-to.

    reply-{uuid}@{domain}

    The UUID contains colons, which aren't allowed in email addresses, so swap those
    out for dollar signs ($) as a placeholder using a string `replace`.  The rest of
    the UUID is base64-encoded, so there will be neither colons nor dollar signs in it
    (it's only alphanumerics, hyphens, and underscores).
    """
    uuid = discussion.generate_reply_uuid(user).replace(':', '$')
    site = get_current_site(request)
    return 'reply-{}@{}'.format(uuid, site)


class CommentEmailMixin:
    """A mixin for CreateViews and similar that build comments."""
    @staticmethod
    def users_to_notify(comment):
        """
        Return subscribers to the comment's discussion or its parent group.

        Exclude anyone who's explicitly ignored this discussion, and the person who
        posted the comment.
        """
        discussion = comment.discussion
        discussion_subscribers = discussion.subscribers.all()
        group_subscribers = discussion.group.watchers.exclude(
            ignored_discussions=discussion
        )

        all_subscribers = discussion_subscribers | group_subscribers
        return all_subscribers.exclude(pk=comment.user.pk)

    def email_subscribers(self, comment):
        """Notify all subscribers to the discussion or its group, except the poster."""
        users = self.users_to_notify(comment)
        for user in users:
            send(
                to=user.email,
                subject=NEW_COMMENT_SUBJECT.format(discussion=comment.discussion.name),
                template_name='groups/emails/new_comment.txt',
                reply_to=get_reply_address(comment.discussion, user, self.request),
                context={
                    'comment': comment,
                    'user': user,
                    'site': get_current_site(self.request),
                    'protocol': 'https' if self.request.is_secure() else 'http',
                },
            )


class CommentPostView(CommentEmailMixin, CreateView):
    """
    Base class for views that post a comment to a particular discussion.

    Must be initialised with form_class and template_name attributes, as required by
    the superclass, CreateView.
    """
    model = models.BaseComment

    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        self.discussion = models.Discussion.objects.select_related('group').get(pk=pk)
        return super(CommentPostView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """Attach the discussion and its existing comments to the context."""
        context = super(CommentPostView, self).get_context_data(*args, **kwargs)
        context['discussion'] = self.discussion
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.discussion = self.discussion
        self.object = form.save()
        self.email_subscribers(self.object)
        return HttpResponseRedirect(self.get_success_url())
