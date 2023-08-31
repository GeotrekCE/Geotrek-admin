============
Contributing
============

Conventions
-----------

* Before contributing, open an issue and discuss about it with community (is it a bug or a feature ? What is the best way to achieve my goal ?)
* Use flake8
* KISS & DRY as much as possible
* Elegant and generic is good, simple is better
* Separate bug fixes and new features in several pull requests.
* Open a new Pull Request in "Draft" status until tests passed. Use at least 'bug', 'improvement' or 'feature' label.
* Commits messages are explicit and mention issue number (``(ref #12)`` or ``(fixes #23)``), they should contains corresponding tag (see below)
* Features are developed in a branch and merged from Github pull-requests.


Definition of done
------------------

* ``docs/changelog.rst`` is up-to-date
* An explicit unit-test covers the bugfix or the new feature.
* A frontend test (:path:jstests/nav-\*.js) covers the navigation bug fix or feature
* A JS *Mocha* test (:path:jstests/tests.\*.js) covers the JavaScript bug fix or feature
* Unit-tests total coverage is above or at least equal with previous commits. Patch coverage is 100% on new lines.
* Settings have default value in ``settings/base.py``
* Installation instructions and documentation are up-to-date

Check TODO in the source tree:

::

   find geotrek | xargs egrep -n -i '(TODO|XXX|temporary|FIXME)'


Pull requests
-------------

Before creating a pull request, ensure you follow thoses rules :

* Follow the guidelines of this page
* Self-review your code
* Add comments in your code, particularly in hard-to-understand areas
* Make corresponding changes to the documentation
* There is tests that prove my fix is effective or that my feature works.
* All new lines of code are tested
* There is an entry in the changelog file

Pull requests are following a naming convention in order to easily establish their perimeter. You can use one of those prefix:

+-----------------+---------------+------------------------+-----------------------+---------+
| Tag             | Branch prefix | Emoji                  | Emoji code            | Unicode |
+=================+===============+========================+=======================+=========+
| Improvements    | impr\_        | :dizzy:                | dizzy                 | 💫      |
+-----------------+---------------+------------------------+-----------------------+---------+
| Bug fixes       | bug\_         | :bug:                  | bug                   | 🐛      |
+-----------------+---------------+------------------------+-----------------------+---------+
| Features        | feat\_        | :sparkles:             | sparkles              | ✨      |
+-----------------+---------------+------------------------+-----------------------+---------+
| Documentation   | doc\_         | :pencil:               | memo                  | 📝      |
+-----------------+---------------+------------------------+-----------------------+---------+
| Maintenance     | maint\_       | :construction_site:    | building_construction | 🏗       |
+-----------------+---------------+------------------------+-----------------------+---------+
| Refactor        | ref\_         | :recycle:              | recycle               | ♻       |
+-----------------+---------------+------------------------+-----------------------+---------+
| Dependencies    | dep\_         | :arrow_up:             | arrow_up              | ⬆       |
+-----------------+---------------+------------------------+-----------------------+---------+
| CI/CD           | cicd\_        | :construction_worker:  | construction_worker   | 👷      |
+-----------------+---------------+------------------------+-----------------------+---------+
| Performances    | perf\_        | :zap:                  | zap                   | ⚡      |
+-----------------+---------------+------------------------+-----------------------+---------+
| Tooling         | tool\_        | :hammer:               | hammer                | 🔨      |
+-----------------+---------------+------------------------+-----------------------+---------+
| UI/UX           | uiux\_        | :lipstick:             | lipstick              | 💄      |
+-----------------+---------------+------------------------+-----------------------+---------+
| Security        | sec\_         | :lock:                 | lock                  | 🔒      |
+-----------------+---------------+------------------------+-----------------------+---------+
| Translations    | trans\_       | :globe_with_meridians: | globe_with_meridians  | 🌐      |
+-----------------+---------------+------------------------+-----------------------+---------+
| Hotfix          | hot\_         | :ambulance:            | ambulance             | 🚑      |
+-----------------+---------------+------------------------+-----------------------+---------+
| Breaking change | break\_       | :boom:                 | boom                  | 💥      |
+-----------------+---------------+------------------------+-----------------------+---------+

Tags used only for commits:

========= =========================== =========================
Tag       Emoji                       Emoji code
========= =========================== =========================
Codestyle :art:                       art
Clean     :fire:                      fire
Tests     :white_check_mark:          white_check_mark
Release   :bookmark:                  bookmark
Merge     :twisted_rightwards_arrows: twisted_rightwards_arrows
========= =========================== =========================


Release
-------

On master branch:

* Update files *VERSION*, *docs/conf.py* and *docs/changelog.rst* to remove ``+dev`` suffix and increment version (please use semver rules)
* Run ``dch -r -D RELEASED``, update version in the same way and save
* Commit with message 'Release x.y.z' and push to ``master``
* Create new release on Github, with tag X.Y.Z, click on "Generate release notes"
* Wait for release to be published through CI
* Update files *VERSION*, *docs/conf.py* and *docs/changelog.rst* to add ``+dev`` suffix
* Run ``dch -v <version>+dev --no-force-save-on-release`` and save
* Commit with message 'Back to development' and push to ```master``

* When creating a new release 'x.y.z' on github, Github actions will generate the .deb package file, and publish it on https://packages.geotrek.fr (see ``.circleci/config.yml`` file for details)
