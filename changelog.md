# Changelog for incuna-groups

This project uses Semantic Versioning (2.0).

## v4.0.2

- Make CommentPostWithAttachment slightly more extensible.

## v4.0.1

- Add a missing migration.

## v4.0.0

- Remove FileComment.
- Improve ordering on the list of groups and a group's discussion list.

## v3.3.0

- Add a new page that allows a user to post a comment with one attached file. This is
  currently linked to from the discussion thread view in lieu of the existing
  "upload a file" page, but the latter hasn't been removed.

## v3.2.1

- Fix a longtime error involving a missing `includes/_pagination.html` template.

## v3.2.0

- Allow admin classes for `incuna-groups`' models to be customised easily through its
  `AppConfig`.

## v3.1.3

- Display group URLs properly in notification emails.

## v3.1.2

- Add methods to the `Group` model that help display useful information.

## v3.1.1

- Improve email template copy.

## v3.1.0

- Add the ability to post files to discussions by attaching them to email replies.
- Improve the display of file comments and make them link to the file in question.
- Add a proper README.

## v3.0.3

- Send `Reply-To` UUIDs in email notifications with the colons replaced with dollar signs,
  since a colon is an illegal character in an email address.
- Fix broken `post()` method in `CommentPostByEmail` so that it will work in practice.

## v3.0.2

- Add new email templates to MANIFEST.in.

## v3.0.1

- Fix urls.py import structure.

## v3.0.0  (Broken, see v3.0.1)

- Refactor `views.py` into several files in the `views` package.  These modules are
  `views._helpers`, `views.comments`, `views.discussions`, `views.groups`, and
  `views.subscriptions`.  You will need to edit any import statements you are making
  to `incuna-groups` views.  (No URLs have changed.)

## v2.0.0

- Use html `buttons` instead of `inputs` for form submission.

## v1.1.0 (Broken, see v3.0.2 and v3.0.3)

- Add the ability to reply to discussions by replying to notification emails.

## v1.0.3

- Add a test project for easier creation of migrations and testing the admin, as well as
  to run the tests themselves.
- Hide `subscribers`, `ignorers` and `watchers` from the admin, since they aren't meant
  to be editable there.
- Make all the `ManyToManyFields` non-required.

## v1.0.2

- Use `filter_horizontal` on many-to-many fields in the admin.

## v1.0.1

- Add `__str__` methods to `Group`, `Discussion` and `BaseComment`.

## v1.0.0

- **Drop Django 1.7 support.**
- Add email notifications for users subscribed to groups and discussions when new
  discussions or comments appear in those.

## v0.6.0

- Add `GroupSubscribe` view.

## v0.5.1

- Add missing migration.

## v0.5.0

- Add support for Django 1.8.
- Relax pinning of dependencies in `setup.py`.

## v0.4.0

- Added new manager methods for accessing groups, discussions, comments and users.
- Added an `AppConfig` in apps.py for ease of configuration.
- Added new manager methods to return recent groups, discussions, and comments.
- Added a mixin that can be added to User managers or querysets to return recent users.

## v0.3.1

- Added `comment.render` to the `Comment` model.
- Simplified the comment related templates.

## v0.3.0

- Add permalinks to comments.
- Comments can now be deleted by the users that made them or admin users.
- Add file comments, allowing users to upload files to discussions.

## v0.2.0

- Implement the ability to subscribe to discussions.
- Add back links to multiple templates.
- De-require `django` again (to test this locally, you'll need to install it manually).

## v0.1.1

- Fix a deployment bug by adding `MANIFEST.in`.
- Add a missing requirement for `django`.

## v0.1

- Initial release.

