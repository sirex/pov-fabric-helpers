Fabric Helpers
==============

This is a collection of helpers we use in Fabric scripts.  They're primarily
intended to manage Ubuntu servers (10.04 LTS, 12.04 LTS or 14.04 LTS).

A possibly-incomplete list of them:

- ``ensure_apt_not_outdated()``
- ``ensure_known_host("hostname ssh-rsa AAA....")``
- ``ensure_user("username")``
- ``git_clone("git@github.com:ProgrammersOfVilnius/project.git", "/opt/project")``
- ``ensure_postgresql_user("username")``
- ``ensure_postgresql_db("dbname", "owner")``
- ``changelog("# Installing stuff")`` (requires pov-admin-tools_)
- ``changelog_append("# more stuff")`` (requires pov-admin-tools_)

.. _pov-admin-tools: https://github.com/ProgrammersOfVilnius/pov-admin-tools


Usage
-----

For now add this repository as a git submodule::

  cd ~/src/project
  git submodule add https://github.com/ProgrammersOfVilnius/pov-fabric-helpers
  git submodule init

and in your ``fabfile.py`` add ::

  sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pov-fabric-helpers'))
  from pov_fabric import ...

Then remind your users to run ``git submodule init`` after they clone the repo
with the fabfile.


Instance management
-------------------

All of my fabfiles can manage several *instances* of a particular service.
Externally this looks like ::

  fab instance1 task1 task2 instance2 task3

which executes Fabric tasks ``task1`` and ``task2`` on instance ``instance1``
and then executes ``task3`` on ``instance2``.

An instance defines various parameters, such as

- what server hosts it
- where on the filesystem it lives
- what Unix user IDs are used
- what database is used for this instance
- etc.

To facilitate this ``pov_fabric`` provides three things:

- an ``Instance`` class that should be subclassed to provide your own instances ::

    from pov_fabric import Instance as BaseInstance

    class Instance(BaseInstance):
        def __init__(self, name, host, home='/opt/sentry', user='sentry',
                     dbname='sentry'):
            super(Instance, self).Instance.__init__(name, host)
            self.home = home
            self.user = user
            self.dbname = dbname

- ``Instance.define()`` that defines new instances and creates tasks for
  selecting them ::

    Instance.define(
        name='testing',
        host='root@vagrantbox',
    )
    Instance.define(
        name='production',
        host='server1.pov.lt',
    )
    Instance.define(
        name='staging',
        host='server1.pov.lt',
        home='/opt/sentry-staging',
        user='sentry-staging',
        dbname='sentry-staging',
    )

- A ``get_instance()`` method that returns the currently selected instance
  (or aborts with an error if the user didn't select one) ::

    from pov_fabric import get_instance

    @task
    def look_around():
        instance = get_instance()
        with settings(host=instance.host):
            run('hostname')


Previously I used a slightly different command style ::

    fab task1:instance1 task2:instance1 task3:instance2

and this can still be supported if you write your tasks like this ::

    @task
    def look_around(instance=None):
        instance = get_instance(instance)
        with settings(host=instance.host):
            run('hostname')

Be careful if you mix styles, e.g. ::

    fab instance1 task1 task2:instance2 task3

will run ``task1`` and ``task3`` on ``instance1`` and it will run ``task2`` on
``instance2``.
