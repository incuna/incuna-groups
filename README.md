# `incuna-groups` [![Build Status](https://magnum.travis-ci.com/incuna/incuna-groups.svg?token=9QKsFUYHUxekS7Q4cLHs&branch=master)](https://travis-ci.org/incuna/incuna-groups)

An extensible Django app that provides forum functionality.  Administrators can create discussion groups.  Users can create discussions on groups, and comment on those discussions.  Users can also subscribe to groups and/or discussions to receive notifications from them, and reply by replying to the notifications. 

## Installation

`incuna-groups` is on PyPI, so you can install it with `pip install incuna-groups`.

This project contains migrations, so run `python manage.py migrate` before using it.

## Usage

`incuna-groups` is self-contained - it provides models, views, and templates.  At the moment, it doesn't provide styling or a REST API.

### Models

- `Group`: A group that contains any number of discussions, like a forum board.  Created in the Django admin, and holds discussion threads added by users.  A group can be denoted as private, in which case a user has to request to join it before they can read or post any comments.  A group can also have moderators who have the ability to delete or edit other users' comments.  Users can subscribe to a group, which will send them notifications for any discussions created on the group or comments posted to discussions in the group.
- `Discussion`: A single discussion thread, with at least one comment on it (the initial one).  Created by a user.  Users can comment on and subscribe to discussions.  If a user is already subscribed to a discussion's parent group, they can "unsubscribe" from the discussion, which will (internally) cause the discussion to be 'ignored' for that user, and they won't get any notifications for it.
- `BaseComment`: A `django-polymorphic` base class for `Comment`s.  Doesn't do anything by itself, but is used for testing and to refer to arbitrary different kinds of comment.  Subclasses of `BaseComment` are picked up by the discussion-related views.  It comes with some subclasses:
  * `TextComment`: A comment with a text body - an entirely ordinary message.
  * `FileComment`: A comment containing an uploaded file.
  
### Views and Admin Pages

There are a lot of different views that come together to make the forums work.

- `Group`
  * Created by `admin.GroupAdmin` - in the Django admin
  * Listed by `views.groups.GroupList`
  * Detailed by `views.groups.GroupDetail` - implemented as a `ListView` for `Discussion`s, to display the group's contents.
- `Discussion`
  * Created by `admin.DiscussionAdmin` - in the Django admin
  * Created by `views.discussions.DiscussionCreate` - this one also creates the `Discussion`'s first comment, currently a `TextComment`.
  * Listed by `views.groups.GroupDetail`
  * Detailed by `views.discussions.DiscussionThread` - implemented as a `CommentPostView` from `views._helpers`, to allow people to reply via the discussion page itself.
- `Comment`
  * Created by `views._helpers.CommentPostView` - a base class that both creates comments and sends email notifications to relevant people.
  * Created by `views.discussions.DiscussionThread` - the discussion thread page provides an inline reply form that submits `TextComment`s.
  * Created by `views.comments.CommentUploadFile` - a separate page for the uploading of `FileComment`s.
  * Created by `views.comments.CommentPostByEmail` - an endpoint suitable for receiving email replies via Mailgun.
  * Listed by `views.discussions.DiscussionThread`
  * Deleted by `views.comments.CommentDelete` - a comment provides a 'delete' button which will archive it and hide its contents from view.

## Features

## Extending `incuna-groups`



Email reply gotchas:
- The `/groups/reply/` endpoint _has a trailing slash_.  Ensure that this slash is included in any Mailgun config otherwise you'll get a stream of HTTP301s.
- If you're using `incuna_auth.LoginRequiredMiddleware`, make sure to add `/groups/reply/` to `LOGIN_EXEMPT_URLS` to avoid more 301s.
