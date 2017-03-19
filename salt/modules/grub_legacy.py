# -*- coding: utf-8 -*-
'''
Support for GRUB Legacy
'''
from __future__ import absolute_import

# Import python libs
import filecmp
import os
import re
import shutil

# Import salt libs
import salt.utils
import salt.utils.decorators as decorators
from salt.exceptions import CommandExecutionError

# Define the module's virtual name
__virtualname__ = 'grub'


def __virtual__():
    '''
    Only load the module if grub is installed
    '''
    if os.path.exists(_detect_conf()):
        return __virtualname__
    return (False, 'The grub_legacy execution module cannot be loaded: '
       'the grub config file does not exist in /boot/grub/')


@decorators.memoize
def _detect_conf():
    '''
    GRUB conf location differs depending on distro
    '''
    if __grains__['os_family'] == 'RedHat':
        return '/boot/grub/grub.conf'
    # Defaults for Ubuntu, Debian, Arch, and others
    return '/boot/grub/menu.lst'


def version():
    '''
    Return server version from grub --version

    CLI Example:

    .. code-block:: bash

        salt '*' grub.version
    '''
    cmd = '/sbin/grub --version'
    out = __salt__['cmd.run'](cmd)
    return out


def conf():
    '''
    Parse GRUB conf file

    CLI Example:

    .. code-block:: bash

        salt '*' grub.conf
    '''
    stanza = ''
    stanzas = []
    in_stanza = False
    ret = {}
    pos = 0
    try:
        with salt.utils.fopen(_detect_conf(), 'r') as _fp:
            for line in _fp:
                if line.startswith('#'):
                    continue
                if line.startswith('\n'):
                    in_stanza = False
                    if 'title' in stanza:
                        stanza += 'order {0}'.format(pos)
                        pos += 1
                        stanzas.append(stanza)
                    stanza = ''
                    continue
                if line.strip().startswith('title'):
                    if in_stanza:
                        stanza += 'order {0}'.format(pos)
                        pos += 1
                        stanzas.append(stanza)
                        stanza = ''
                    else:
                        in_stanza = True
                if in_stanza:
                    stanza += line
                if not in_stanza:
                    key, value = _parse_line(line)
                    ret[key] = value
            if in_stanza:
                if not line.endswith('\n'):
                    line += '\n'
                stanza += line
                stanza += 'order {0}'.format(pos)
                pos += 1
                stanzas.append(stanza)
    except (IOError, OSError) as exc:
        msg = "Could not read grub config: {0}"
        raise CommandExecutionError(msg.format(str(exc)))

    ret['stanzas'] = []
    for stanza in stanzas:
        mydict = {}
        for line in stanza.strip().splitlines():
            key, value = _parse_line(line)
            mydict[key] = value
        ret['stanzas'].append(mydict)
    return ret


def _parse_line(line=''):
    '''
    Used by conf() to break config lines into
    name/value pairs
    '''
    parts = line.split()
    key = parts.pop(0)
    value = ' '.join(parts)
    return key, value


def cmdline_present(name, value=None, backup=False):
    '''
    Add a kernel cmdline parameter to the GRUB conf file

    The first parameter is the kernel cmdline parameter.

    The second parameter is the value for parameters which
    accept an equal sign (=). This is optional.

    CLI Example:

    .. code-block:: bash

        salt '*' grub.cmdline_present 'quiet'

        salt '*' grub.cmdline_present 'elevator' 'deadline'
    '''
    paramstring = str(name)
    valuestring = str(value)
    backup_ext = '.bak'

    if value:
        searchstring = paramstring + '=' + valuestring
    else:
        searchstring = paramstring

    grub_conf = _detect_conf()
    temp_file = grub_conf + '.writing'

    try:
        with salt.utils.fopen(temp_file, 'w') as _newfile:
            try:
                with salt.utils.fopen(grub_conf, 'r') as _oldfile:
                    for line in _oldfile:
                        if line.lstrip().startswith('kernel'):
                            if not searchstring in line:
                                if paramstring in line:
                                    line = re.sub(paramstring + '=\S+', searchstring, line)
                                else:
                                    line = line.rstrip() + ' ' + searchstring + '\n'
                        _newfile.write(line)
            except (IOError, OSError) as exc:
                msg = "Could not read grub config: {0}"
                raise CommandExecutionError(msg.format(str(exc)))
        if not filecmp.cmp(grub_conf, temp_file):
            if backup:
                shutil.copy2(grub_conf, grub_conf + backup_ext)
            shutil.copyfile(temp_file, grub_conf)
        os.remove(temp_file)
            
    except (IOError, OSError) as exc:
        msg = "Could not write to temporary file: {0}"
        raise CommandExecutionError(msg.format(str(exc)))

    return conf()
