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
