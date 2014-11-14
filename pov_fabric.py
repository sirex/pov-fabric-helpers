"""
Fabric helpers
"""

import posixpath
from pipes import quote  # TBD: use shlex.quote on Python 3.2+

from fabric.api import run, sudo, quiet, settings, cd
from fabric.contrib.files import exists, append


#
# System management helpers
#

def ensure_apt_not_outdated():
    """Make sure apt-get update was run within the last day."""
    if not run("find /var/lib/apt/lists -maxdepth 0 -mtime -1", quiet=True):
        sudo("apt-get update -qq")


def ensure_known_host(host_key, known_hosts='/root/.ssh/known_hosts'):
    """Make sure a host key exists in the known_hosts file.

    This is idempotent: running it again won't add the same key again.
    """
    if not exists(known_hosts, use_sudo=True):
        if not exists(posixpath.dirname(known_hosts), use_sudo=True):
            sudo('install -d -m700 %s' % posixpath.dirname(known_hosts))
        sudo('touch %s' % known_hosts)
    # Must use shell=True to work around Fabric bug, where it would fall
    # flat in contains() with an error ("sudo: export: command not
    # found") that is silently suppressed, resulting in always appending
    # the ssh key to /root/.ssh/known_hosts.  Probably because I use
    # `with settings(shell_env(LC_ALL='C.UTF-8')):`.
    append(known_hosts, host_key, use_sudo=True, shell=True)


def ensure_user(user):
    """Create a system user if it doesn't exist already.

    This is idempotent: running it again won't add the same user again.
    """
    with quiet():
        if run("id {user}".format(user=user)).succeeded:
            return
    with settings(sudo_user="root"):
        sudo("adduser --system --group --disabled-password --quiet %s" % user)


#
# Git
#

def git_clone(git_repo, work_dir, force=False):
    """Clone a git repository into work_dir.

    If work_dir exists and force is False (default), aborts.

    If work_dir exists and force is True, performs a 'git fetch' followed by
    'git reset origin/master'.

    Takes care to allow SSH agent forwarding to be used for authentication.

    Returns the commit hash of the version cloned.
    """
    # sudo removes SSH_AUTH_SOCK from the environment, so we can't make use of
    # the ssh agent forwarding unless we cunningly preserve the envvar and sudo
    # to root (because only root and the original user will be able to access
    # the socket)
    ssh_auth_sock = run("echo $SSH_AUTH_SOCK", quiet=True)
    if exists(posixpath.join(work_dir, '.git')) and force:
        with cd(work_dir):
            sudo("SSH_AUTH_SOCK={ssh_auth_sock} git fetch".format(
                ssh_auth_sock=ssh_auth_sock))
            sudo("git reset origin/master")
    else:
        sudo("SSH_AUTH_SOCK={ssh_auth_sock} git clone {git_repo} {work_dir}".format(
            ssh_auth_sock=ssh_auth_sock,
            git_repo=git_repo,
            work_dir=work_dir))
    with cd(work_dir):
        got_commit = sudo("git describe --always").strip()
    return got_commit


#
# PostgreSQL helper
#

def postgresql_user_exists(user):
    """Check if a postgresql user already exists."""
    out = sudo("psql -tAc \"SELECT 1 FROM pg_roles WHERE rolname = '%s'\"" % user,
               user='postgres', quiet=True)
    return bool(out)


def ensure_postgresql_user(user):
    """Create a PostgreSQL user if it doesn't exist already.

    This is idempotent: running it again won't add the same user again.
    """
    if not postgresql_user_exists(user):
        sudo("LC_ALL=C.UTF-8 createuser -DRS %s" % user, user='postgres')


def postgresql_db_exists(dbname):
    """Check if a PostgreSQL database already exists."""
    out = sudo("psql -tAc \"SELECT 1 FROM pg_database WHERE datname = '%s'\"" % dbname,
               user='postgres', quiet=True)
    return bool(out)


def ensure_postgresql_db(dbname, owner):
    """Create a PostgreSQL database if it doesn't exist already.

    This is idempotent: running it again won't create the database again.
    """
    if not postgresql_db_exists(dbname):
        sudo("LC_ALL=C.UTF-8 createdb -E utf-8 -T template0 -O %s %s" % (owner, dbname),
             user='postgres')


#
# pov-admin-tools
#

def changelog(message, append=False, optional=True):
    """Append a message to /root/Changelog, with a timestamped header.

    Depends on pov-admin-tools.  If it's not installed, skips the
    message (unless you say optional=False, in which case it aborts
    with an error).

    By default the message gets a timestamped header.  Use append=True
    to append to an existing message instead of starting a new one.
    """
    if exists('/usr/sbin/new-changelog-entry') or not optional:
        cmd = 'new-changelog-entry'
        if append:
            cmd += ' -a'
        cmd += ' ' + quote(message)
        sudo(cmd, user='root')


def changelog_append(message):
    """Append a message to /root/Changelog.

    Shortcut for changelog(message, append=True).
    """
    changelog(message, append=True)

