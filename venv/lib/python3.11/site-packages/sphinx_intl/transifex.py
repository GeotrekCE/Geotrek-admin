# -*- coding: utf-8 -*-

import os
import re
import subprocess
import textwrap
from pathlib import Path
from shutil import which

import click

from .catalog import load_po


# ==================================
# settings

TRANSIFEX_CLI_MINIMUM_VERSION = (1, 2, 1)

# To avoid using invalid resource name, append underscore to such names.
# As a limitation, append `_` doesn't care about collision to other resources.
# e.g. 'glossary' and 'glossary_' are pushed as a 'glossary_'. The following
# resource names are reserved slugs, Transifex will reply with an error on these
# resource names.
IGNORED_RESOURCE_NAMES = (
    'glossary',
    'settings',
)

TRANSIFEXRC_TEMPLATE = """\
[https://www.transifex.com]
rest_hostname = https://rest.api.transifex.com
token = %(transifex_token)s
"""

TXCONFIG_TEMPLATE = """\
[main]
host = https://www.transifex.com
"""


# ==================================
# utility functions

def normalize_resource_name(name):
    # replace path separator with '--'
    name = re.sub(r'[\\/]', '--', name)

    # replace unusable characters (not: -, _ ascii, digit) with '_'
    name = re.sub(r'[^\-\w]', '_', name)

    # append `_` for ignored resource names
    while name in IGNORED_RESOURCE_NAMES:
        name += '_'

    return name


def check_transifex_cli_installed():
    tx_cli_url = 'https://raw.githubusercontent.com/transifex/cli/master/install.sh'
    if not which("tx"):
        msg = textwrap.dedent(f"""\
            Could not run "tx".
            You need to install the Transifex CLI external library.
            Please install the below command and restart your terminal \
            if you want to use this action:

                $ curl -o- {tx_cli_url} | bash

            """)
        raise click.BadParameter(msg)

    version_msg = subprocess.check_output("tx --version", shell=True, encoding="utf-8")

    if not version_msg.startswith("TX Client"):
        msg = textwrap.dedent(f"""\
            The old transifex_client library was found.
            You need to install the Transifex CLI external library.
            Please install the below command and restart your terminal \
            if you want to use this action:

                $ curl -o- {tx_cli_url} | bash

            """)
        raise click.BadParameter(msg)

    version = tuple(int(x) for x in version_msg.split("=")[-1].strip().split("."))

    if not version >= TRANSIFEX_CLI_MINIMUM_VERSION:
        msg = textwrap.dedent(f"""\
        An unsupported version of the Transifex CLI was found.
        Version {TRANSIFEX_CLI_MINIMUM_VERSION} or greater is required.
        Please run the below command if you want to use this action:

            $ tx update

        """)
        raise click.BadParameter(msg)


# ==================================
# commands

def create_transifexrc(transifex_token):
    """
    Create `$HOME/.transifexrc`
    """
    target = os.path.normpath(os.path.expanduser('~/.transifexrc'))

    if os.path.exists(target):
        click.echo('{0} already exists, skipped.'.format(target))
        return

    if not transifex_token:
        msg = textwrap.dedent("""\
        You need a transifex token by command option or environment.
        command option: --transifex-token
        """)
        raise click.BadParameter(msg, param_hint='transifex_token')

    with open(target, 'wt') as rc:
        rc.write(TRANSIFEXRC_TEMPLATE % locals())
    click.echo('Create: {0}'.format(target))


def create_txconfig():
    """
    Create `./.tx/config`
    """
    target = os.path.normpath('.tx/config')
    if os.path.exists(target):
        click.echo('{0} already exists, skipped.'.format(target))
        return

    if not os.path.exists('.tx'):
        os.mkdir('.tx')

    with open(target, 'wt') as f:
        f.write(TXCONFIG_TEMPLATE)

    click.echo('Create: {0}'.format(target))


def update_txconfig_resources(transifex_organization_name, transifex_project_name,
                              locale_dir, pot_dir):
    """
    Update resource sections of `./.tx/config`.
    """
    check_transifex_cli_installed()

    cmd_tmpl = (
        'tx',
        'add',
        '--organization', '%(transifex_organization_name)s',
        '--project', '%(transifex_project_name)s',
        '--resource', '%(resource_slug)s',
        '--resource-name', '%(resource_name)s',
        '--file-filter', '%(locale_dir)s/<lang>/LC_MESSAGES/%(resource_path)s.po',
        '--type', 'PO',
        '%(pot_dir)s/%(resource_path)s.pot',
    )

    # convert transifex_project_name to internal name
    transifex_project_name = transifex_project_name.replace(' ', '-')
    transifex_project_name = re.sub(r'[^\-_\w]', '', transifex_project_name)

    pot_dir = Path(pot_dir)
    pot_paths = sorted(pot_dir.glob('**/*.pot'))
    with click.progressbar(
        pot_paths,
        length=len(pot_paths),
        color="green",
        label="adding pots...",
        item_show_func=lambda p: str(p),
    ) as progress_bar:
        for pot_path in progress_bar:
            resource_path = str(pot_path.relative_to(pot_dir).with_suffix(''))
            resource_slug = resource_name = normalize_resource_name(resource_path)
            pot = load_po(str(pot_path))
            if len(pot):
                lv = locals()
                cmd = [arg % lv for arg in cmd_tmpl]
                subprocess.check_output(cmd, shell=False)
            else:
                click.echo('{0} is empty, skipped'.format(pot_path))
