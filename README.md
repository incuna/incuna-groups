# `incuna-groups` [![Build Status](https://magnum.travis-ci.com/incuna/incuna-groups.svg?token=9QKsFUYHUxekS7Q4cLHs&branch=master)](https://travis-ci.org/incuna/incuna-groups)

An extensible Django app, that provides forum functionality.
- Create groups.
- Create discussions on groups.
- Comment on discussions.

Email reply gotchas:
- The `/groups/reply/` endpoint _has a trailing slash_.  Ensure that this slash is included in any Mailgun config otherwise you'll get a stream of HTTP301s.
- If you're using `incuna_auth.LoginRequiredMiddleware`, make sure to add `/groups/reply/` to `LOGIN_EXEMPT_URLS` to avoid more 301s.
