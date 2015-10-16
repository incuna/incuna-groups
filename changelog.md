v0.5.0
------
* Add support for Django 1.8.
* Relax pinning of dependencies in `setup.py`.

v0.4.0
------
* Added new manager methods for accessing groups, discussions, comments and users.
* Added an `AppConfig` in apps.py for ease of configuration.
* Added new manager methods to return recent groups, discussions, and comments.
* Added a mixin that can be added to User managers or querysets to return recent users.

v0.3.1
------
* Added `comment.render` to the `Comment` model.
* Simplified the comment related templates.

v0.3.0
------
* Add permalinks to comments.
* Comments can now be deleted by the users that made them or admin users.
* Add file comments, allowing users to upload files to discussions.

v0.2.0
------
* Implement the ability to subscribe to discussions.
* Add back links to multiple templates.
* De-require `django` again (to test this locally, you'll need to install it manually).

v0.1.1
------
* Fix a deployment bug by adding `MANIFEST.in`.
* Add a missing requirement for `django`.

v0.1
----
* Initial release.

