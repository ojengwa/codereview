Paylogic Codereview
===================

`Paylogic Codereview` allows you to run Rietveld - the code review tool
available at http://codereview.appspot.com/.
However, it's a highly customized version of Rietveld. It contains several useful additions,
bugfixes as well.

If you want to use it, please read the documentation below.

.. image:: https://api.travis-ci.org/paylogic/codereview.png
   :target: https://travis-ci.org/paylogic/codereview
.. image:: https://coveralls.io/repos/paylogic/codereview/badge.png?branch=master
   :target: https://coveralls.io/r/paylogic/codereview


Custom features implemented
-------------------------------

* Creation or update of the codereview issue using the remote repositories automatically, parameters are taken from
  given `Fogbugz <https://www.fogcreek.com/fogbugz/>`_ case

* Approve patchset for further merging, implemented also through the integration with Fogbugz

* Improved django admin to simplify user management and other administrative tasks

* Fogbugz authentication integrated

* Bugfixes related to deployment on local server, not Google App Engine

* Main functionality covered with tests


Development Environment
-----------------------

To set up the development environment, run:

::

    # install system dependencies, requires sudo access!
    make dependencies

    # install python dependencies, initialize configs
    make develop


Then, to run the codereview server:

::

    env/bin/python manage.py runserver

Open a browser, go to http://127.0.0.1:8000/ and you can use the codereview tool.

You'll need to grant some permissions for your user(s) authenticated through fogbugz:

* `codereview.add_issue` - create issue
* `codereview.view_issue` - view issue
* `codereview.change_comment` - change comment
* `codereview.add_comment` - add comment
* `codereview.approve_patchset` - approve patchset (by Gatekeepers)


Production Deployment
---------------------

::

    make build index_url=<pypi index containing custom package versions>

This command will make ./build folder containing all needed to run the application.

Several python dependencies are for now released only to our corporate pypi index, which is not public.
However, the code of those version is absolutely public, because it's just forks & fixes.
Here is the list of repository locations:

* django-gae2django==0.2paylogic2 - https://code.google.com/r/bubenkoff-gae2django/source/browse/?name=urlquote-login-urls

Until we'll make public corporate pypi server, you can make your own releases or just install them in editable mode

The preferred method to deploy Django applications is to use WSGI supporting
web server. Use ``build/wsgi.py`` file as WSGI script.

There is one important thing to remember. Django serves media (static) files
only in development mode. For running Rietveld in a production environment,
you need to setup your web-server to serve the /static/ alias directly from the ``./build/static_build`` folder.

http://docs.djangoproject.com/en/dev/howto/deployment/modpython/#serving-media-files

There is the example configuration for running Rietveld with Apache2+mod_wsgi
Feel free to copy it from apache.conf.example. You may need to change
'codereview' user name in WSGI directives and adjust paths to match your
installation.

When running in a production environment, keep in Django's CSRF
protection is disabled in this example!


Using wheels
------------

To speedup the build process, 2 make targets are implemented:

`make wheel`
    Build `wheels <https://pypi.python.org/pypi/wheel>`_ for all python dependencies, storing them in the
    cache directory

`make upload-wheel` (depends on `make wheel`)
    Upload previously generated wheels to given private `devpi server <https://pypi.python.org/pypi/devpi-server>`_.

    Parameters:
* `devpi_url` - devpi server URL to use
* `devpi_path` - index path to upload to
* `devpi_login` - login to use for devpi authorization
* `devpi_password` - password to use for devpi authorization

After you'll upload wheels, `make build` and `make develop` time will be dramatically reduced, if you will
pass `index_url` parameter pointing to the same devpi server index you used for `make upload-wheel`, for example:

::

    make build index_url=https://my.pypi.com/index/trusty/+simple/

Be aware that binary wheels can only be used on exactly same architecture and environment as they were built.


Creating the local environment
------------------------------

In order to create new issues - with patches, descriptions and so on - you need
to create the local environment.

First of all, you need to create a local settings file.
This can be done by copying example one:

::

    cp paylogic/settings_local_example.py paylogic/settings_local.py


The most important settings are:

DATABASES
   see django documentation about it

DEBUG
   self-describing

VCS
   dictionary of vcs-specific settings, folder prefix, regular expression of the branch definition, etc,
   see `settings_base.py` config for an example

FEATURE_BRANCH_DEFAULT_PREFIX
   prefix to try to add to feature branch value taken from fogbugz case field, allows to
   shorten feature branch definition

ORIGINAL_BRANCH_DEFAULT_PREFIX
   prefix to try to add to feature branch value taken from fogbugz case field, allows to
   shorten feature branch definition

TEMP_FOLDER
   temporary folder used to clone and export repositories

FOGBUGZ_URL
   URL of your fogbugz instance

AUTH_FOGBUGZ_SERVER
   URL of your fogbugz instance

FOGBUGZ_TOKEN
   Fogbugz user API token to be used for Fogbugz API calls

API_TOKEN
   authorization token for few paylogic custom API methods exposed by codereview

FOGBUGZ_MERGEKEEPER_USER_ID
   Fogbugz user ID. Used to assign an approved codereview's case to

FOGBUGZ_APPROVED_REVISION_FIELD_ID
   Fogbugz field id to get and set approved revision information on the case

FOGBUGZ_TARGET_BRANCH_FIELD_ID
   Fogbugz field id to set target branch value. Used for mergekeepering process

FOGBUGZ_ORIGINAL_BRANCH_FIELD_ID
   Fogbugz field id to get original branch URL to create or update codereview issue

FOGBUGZ_FEATURE_BRANCH_FIELD_ID
   Fogbugz field id to get feature branch URL to create or update codereview issue

FOGBUGZ_CI_PROJECT_FIELD_ID
   Fogbugz field id to get CI project field values. Used for mergekeepering process

FOGBUGZ_APPROVED_TAG
   Fogbugz case tag to set when the case is approved by the gatekeeper

CODEREVIEW_IGNORED_FILES
   List of files to ignore when creating or updating the codereview issue

CODEREVIEW_MAX_FILE_SIZE
   Maximum file size over which file will be consirered as blob, so it's text will not be
   shown as review context, only download will be possible

CODEREVIEW_VALIDATORS
   List of functions, which will be executed to check if generated diff is valid. Functions
   should receive single string argument - full diff.

CODEREVIEW_TARGET_BRANCH_CHOICES_GETTER
   Function to get autompletion list for the target branch field in the gatekeeper approval form.
   Prototype is (ci_project, original_branch, target_branch, branches)

For the defaults of the listed settings, see `<paylogic/settings_base.py>`_.


Paylogic notes
--------------

Paylogic customizations are mostly located in paylogic folder.
However, we also had to change some parts of codereview package.


Database migrations
-------------------

It's problematic to use automatic database migrations tools as codereview app uses google app engine models.
Here is the simple but working solution we've made:

::

     cat paylogic/migrations/*.sql | ./manage.py dbshell

SQL scripts in paylogic/migrations folder are named in order so this way we ensure the correct order of migrations.
Idempotency is ensured by using `IF NOT EXISTS` or similar inside of SQL scripts.


Adding Users
------------

Go to /admin URL and login as a super user. Users may change password by
going to /admin/password_change URL.


License
-------

This software is licensed under the `Apache 2 license <http://www.apache.org/licenses/LICENSE-2.0>`_


© 2014 Paylogic International.
