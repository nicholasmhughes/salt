# -*- coding: utf-8 -*-
'''
Management of GRUB configs
==========================

If GRUB is installed, this state can be used
to manage the GRUB config file.

.. code-block:: yaml

    elevator_deadline:
        grub.cmdline_present:
          - name: elevator
          - value: deadline

.. note::
    Use of these states require that the :mod:`grub <salt.modules.grub>`
    execution module is available.
'''

# Import python libs
import re

# Import Salt libs
from salt.exceptions import CommandExecutionError

def __virtual__():
    '''
    Only make this state available if the grub module is available.
    '''
    return 'grub' if 'grub.conf' in __salt__ else False


def cmdline_present(name, value=None, backup=False):
    '''
    Ensure a kernel cmdline parameter is in the GRUB configuration file.

    name
        The name of the cmdline parameter to pass. In a parameter such as
        ``elevator=deadline``, the name is ``elevator``.

    value
        The value of the cmdline parameter to pass. In a parameter such as
        ``elevator=deadline``, the value is ``deadline``. Parameters without
        values, such as ``quiet``, would just omit the value.

    backup : False
        Whether or not to create a ``.bak`` backup of the GRUB configuration
        when making changes.
    '''
    new_lines = []
    old_lines = []
    paramstring = str(name)
    valuestring = str(value)

    if value:
        searchstring = paramstring + '=' + valuestring
    else:
        searchstring = paramstring

    ret = {'name': name,
           'result': False,
           'comment': '',
           'changes': {}}

    config = __salt__['grub.conf']()

    for stanza in config.get('stanzas', {}):
        if not searchstring in stanza['kernel']:
            old_lines.append(stanza['kernel'])

    for line in old_lines:
        if paramstring in line:
            new_lines.append(re.sub(paramstring + '=\S*', searchstring, line))
        else:
            new_lines.append(line + ' ' + searchstring)

    if not old_lines:
        ret['result'] = True
        ret['comment'] = 'Kernel cmdline already contains {0}'.format(searchstring)

        return ret

    if __opts__['test']:
        ret['comment'] = 'Kernel cmdline is set to be changed to:\n{0}'.format(
                '\n'.join(new_lines))
        ret['result'] = None
        ret['changes'] = {'old': old_lines,
                          'new': new_lines}
        return ret

    try:
        __salt__['grub.cmdline_present'](name, value, backup)

        ret['result'] = True
        ret['comment'] = 'Kernel cmdline has been changed to:\n{0}'.format(
                '\n'.join(new_lines))
        ret['changes'] = {'old': old_lines,
                          'new': new_lines}
    except CommandExecutionError as exc:
        ret['comment'] = 'Failed: {0}'.format(exc)

    return ret
