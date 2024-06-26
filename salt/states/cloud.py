"""
Using states instead of maps to deploy clouds
=============================================

.. versionadded:: 2014.1.0

Use this minion to spin up a cloud instance:

.. code-block:: yaml

    my-ec2-instance:
      cloud.profile:
        my-ec2-config
"""

import pprint

import salt.utils.cloud as suc


def __virtual__():
    """
    Only load if the cloud module is available in __salt__
    """
    if "cloud.profile" in __salt__:
        return True
    return (False, "cloud module could not be loaded")


def _check_name(name):
    ret = {"name": name, "changes": {}, "result": None, "comment": ""}
    if suc.check_name(name, "a-zA-Z0-9._-"):
        ret["comment"] = "Invalid characters in name."
        ret["result"] = False
        return ret
    else:
        ret["result"] = True
        return ret


def _valid(name, comment="", changes=None):
    if not changes:
        changes = {}
    return {"name": name, "result": True, "changes": changes, "comment": comment}


def _get_instance(names):
    # for some reason loader overwrites __opts__['test'] with default
    # value of False, thus store and then load it again after action
    test = __opts__.get("test", False)
    instance = __salt__["cloud.action"](fun="show_instance", names=names)
    __opts__["test"] = test
    return instance


def present(name, cloud_provider, onlyif=None, unless=None, opts=None, **kwargs):
    """
    Spin up a single instance on a cloud provider, using salt-cloud. This state
    does not take a profile argument; rather, it takes the arguments that would
    normally be configured as part of the state.

    Note that while this function does take any configuration argument that
    would normally be used to create an instance, it will not verify the state
    of any of those arguments on an existing instance. Stateful properties of
    an instance should be configured using their own individual state (i.e.,
    cloud.tagged, cloud.untagged, etc).

    name
        The name of the instance to create

    cloud_provider
        The name of the cloud provider to use

    onlyif
        Do run the state only if is unless succeed

    unless
        Do not run the state at least unless succeed

    opts
        Any extra opts that need to be used
    """
    ret = {"name": name, "changes": {}, "result": None, "comment": ""}

    retcode = __salt__["cmd.retcode"]
    if onlyif is not None:
        if not isinstance(onlyif, str):
            if not onlyif:
                return _valid(name, comment="onlyif condition is false")
        elif isinstance(onlyif, str):
            if retcode(onlyif, python_shell=True) != 0:
                return _valid(name, comment="onlyif condition is false")
    if unless is not None:
        if not isinstance(unless, str):
            if unless:
                return _valid(name, comment="unless condition is true")
        elif isinstance(unless, str):
            if retcode(unless, python_shell=True) == 0:
                return _valid(name, comment="unless condition is true")

    # provider=None not cloud_provider because
    # need to ensure ALL providers don't have the instance
    if __salt__["cloud.has_instance"](name=name, provider=None):
        ret["result"] = True
        ret["comment"] = f"Already present instance {name}"
        return ret

    if __opts__["test"]:
        ret["comment"] = f"Instance {name} needs to be created"
        return ret

    info = __salt__["cloud.create"](cloud_provider, name, opts=opts, **kwargs)
    if info and "Error" not in info:
        ret["changes"] = info
        ret["result"] = True
        ret["comment"] = (
            "Created instance {} using provider {} and the following options: {}".format(
                name, cloud_provider, pprint.pformat(kwargs)
            )
        )
    elif info and "Error" in info:
        ret["result"] = False
        ret["comment"] = "Failed to create instance {} using profile {}: {}".format(
            name,
            profile,
            info["Error"],
        )
    else:
        ret["result"] = False
        ret["comment"] = (
            "Failed to create instance {} using profile {}, "
            "please check your configuration".format(name, profile)
        )
    return ret


def absent(name, onlyif=None, unless=None):
    """
    Ensure that no instances with the specified names exist.

    CAUTION: This is a destructive state, which will search all
    configured cloud providers for the named instance,
    and destroy it.

    name
        The name of the instance to destroy

    onlyif
        Do run the state only if is unless succeed

    unless
        Do not run the state at least unless succeed

    """
    ret = {"name": name, "changes": {}, "result": None, "comment": ""}
    retcode = __salt__["cmd.retcode"]

    if onlyif is not None:
        if not isinstance(onlyif, str):
            if not onlyif:
                return _valid(name, comment="onlyif condition is false")
        elif isinstance(onlyif, str):
            if retcode(onlyif, python_shell=True) != 0:
                return _valid(name, comment="onlyif condition is false")
    if unless is not None:
        if not isinstance(unless, str):
            if unless:
                return _valid(name, comment="unless condition is true")
        elif isinstance(unless, str):
            if retcode(unless, python_shell=True) == 0:
                return _valid(name, comment="unless condition is true")

    if not __salt__["cloud.has_instance"](name=name, provider=None):
        ret["result"] = True
        ret["comment"] = f"Already absent instance {name}"
        return ret

    if __opts__["test"]:
        ret["comment"] = f"Instance {name} needs to be destroyed"
        return ret

    info = __salt__["cloud.destroy"](name)
    if info and "Error" not in info:
        ret["changes"] = info
        ret["result"] = True
        ret["comment"] = f"Destroyed instance {name}"
    elif "Error" in info:
        ret["result"] = False
        ret["comment"] = "Failed to destroy instance {}: {}".format(
            name,
            info["Error"],
        )
    else:
        ret["result"] = False
        ret["comment"] = f"Failed to destroy instance {name}"
    return ret


def profile(name, profile, onlyif=None, unless=None, opts=None, **kwargs):
    """
    Create a single instance on a cloud provider, using a salt-cloud profile.

    Note that while profiles used this function do take any configuration
    argument that would normally be used to create an instance using a profile,
    this state will not verify the state of any of those arguments on an
    existing instance. Stateful properties of an instance should be configured
    using their own individual state (i.e., cloud.tagged, cloud.untagged, etc).

    name
        The name of the instance to create

    profile
        The name of the cloud profile to use

    onlyif
        Do run the state only if is unless succeed

    unless
        Do not run the state at least unless succeed

    kwargs
        Any profile override or addition

    opts
        Any extra opts that need to be used
    """
    ret = {"name": name, "changes": {}, "result": None, "comment": ""}
    retcode = __salt__["cmd.retcode"]
    if onlyif is not None:
        if not isinstance(onlyif, str):
            if not onlyif:
                return _valid(name, comment="onlyif condition is false")
        elif isinstance(onlyif, str):
            if retcode(onlyif, python_shell=True) != 0:
                return _valid(name, comment="onlyif condition is false")
    if unless is not None:
        if not isinstance(unless, str):
            if unless:
                return _valid(name, comment="unless condition is true")
        elif isinstance(unless, str):
            if retcode(unless, python_shell=True) == 0:
                return _valid(name, comment="unless condition is true")
    instance = _get_instance([name])
    if instance and not any("Not Actioned" in key for key in instance):
        ret["result"] = True
        ret["comment"] = f"Already present instance {name}"
        return ret

    if __opts__["test"]:
        ret["comment"] = f"Instance {name} needs to be created"
        return ret

    info = __salt__["cloud.profile"](profile, name, vm_overrides=kwargs, opts=opts)

    # get either {Error: ''} or {namestring: {Error: ''}}
    # which is what we can get from providers returns
    main_error = info.get("Error", "")
    name_error = ""
    if isinstance(info, dict):
        subinfo = info.get(name, {})
        if isinstance(subinfo, dict):
            name_error = subinfo.get("Error", None)
    error = main_error or name_error
    if info and not error:
        node_info = info.get(name)
        ret["result"] = True
        default_msg = "Created instance {} using profile {}".format(
            name,
            profile,
        )
        # some providers support changes
        if "changes" in node_info:
            ret["changes"] = node_info["changes"]
            ret["comment"] = node_info.get("comment", default_msg)
        else:
            ret["changes"] = info
            ret["comment"] = default_msg
    elif error:
        ret["result"] = False
        ret["comment"] = "Failed to create instance {} using profile {}: {}".format(
            name,
            profile,
            f"{main_error}\n{name_error}\n".strip(),
        )
    else:
        ret["result"] = False
        ret["comment"] = "Failed to create instance {} using profile {}".format(
            name,
            profile,
        )
    return ret


def volume_present(name, provider=None, **kwargs):
    """
    Check that a block volume exists.
    """
    ret = _check_name(name)
    if not ret["result"]:
        return ret

    volumes = __salt__["cloud.volume_list"](provider=provider)

    if name in volumes:
        ret["comment"] = f"Volume exists: {name}"
        ret["result"] = True
        return ret
    elif __opts__["test"]:
        ret["comment"] = f"Volume {name} will be created."
        ret["result"] = None
        return ret

    response = __salt__["cloud.volume_create"](names=name, provider=provider, **kwargs)
    if response:
        ret["result"] = True
        ret["comment"] = f"Volume {name} was created"
        ret["changes"] = {"old": None, "new": response}
    else:
        ret["result"] = False
        ret["comment"] = f"Volume {name} failed to create."
    return ret


def volume_absent(name, provider=None, **kwargs):
    """
    Check that a block volume exists.
    """
    ret = _check_name(name)
    if not ret["result"]:
        return ret

    volumes = __salt__["cloud.volume_list"](provider=provider)

    if name not in volumes:
        ret["comment"] = "Volume is absent."
        ret["result"] = True
        return ret
    elif __opts__["test"]:
        ret["comment"] = f"Volume {name} will be deleted."
        ret["result"] = None
        return ret

    response = __salt__["cloud.volume_delete"](names=name, provider=provider, **kwargs)
    if response:
        ret["result"] = True
        ret["comment"] = f"Volume {name} was deleted"
        ret["changes"] = {"old": volumes[name], "new": response}
    else:
        ret["result"] = False
        ret["comment"] = f"Volume {name} failed to delete."
    return ret


def volume_attached(name, server_name, provider=None, **kwargs):
    """
    Check if a block volume is attached.
    """
    ret = _check_name(name)
    if not ret["result"]:
        return ret

    ret = _check_name(server_name)
    if not ret["result"]:
        return ret

    volumes = __salt__["cloud.volume_list"](provider=provider)
    instance = __salt__["cloud.action"](fun="show_instance", names=server_name)

    if name in volumes and volumes[name]["attachments"]:
        volume = volumes[name]
        ret["comment"] = "Volume {name} is already attached: {attachments}".format(
            **volumes[name]
        )
        ret["result"] = True
        return ret
    elif name not in volumes:
        ret["comment"] = f"Volume {name} does not exist"
        ret["result"] = False
        return ret
    elif not instance:
        ret["comment"] = f"Server {server_name} does not exist"
        ret["result"] = False
        return ret
    elif __opts__["test"]:
        ret["comment"] = f"Volume {name} will be will be attached."
        ret["result"] = None
        return ret

    response = __salt__["cloud.volume_attach"](
        provider=provider, names=name, server_name=server_name, **kwargs
    )
    if response:
        ret["result"] = True
        ret["comment"] = f"Volume {name} was created"
        ret["changes"] = {"old": volumes[name], "new": response}
    else:
        ret["result"] = False
        ret["comment"] = f"Volume {name} failed to attach."
    return ret


def volume_detached(name, server_name=None, provider=None, **kwargs):
    """
    Check if a block volume is attached.

    Returns True if server or Volume do not exist.
    """
    ret = _check_name(name)
    if not ret["result"]:
        return ret

    if server_name is not None:
        ret = _check_name(server_name)
        if not ret["result"]:
            return ret

    volumes = __salt__["cloud.volume_list"](provider=provider)
    if server_name:
        instance = __salt__["cloud.action"](fun="show_instance", names=[name])
    else:
        instance = None

    if name in volumes and not volumes[name]["attachments"]:
        volume = volumes[name]
        ret["comment"] = "Volume {name} is not currently attached to anything.".format(
            **volumes[name]
        )
        ret["result"] = True
        return ret
    elif name not in volumes:
        ret["comment"] = f"Volume {name} does not exist"
        ret["result"] = True
        return ret
    elif not instance and server_name is not None:
        ret["comment"] = f"Server {server_name} does not exist"
        ret["result"] = True
        return ret
    elif __opts__["test"]:
        ret["comment"] = f"Volume {name} will be will be detached."
        ret["result"] = None
        return ret

    response = __salt__["cloud.volume_detach"](
        provider=provider, names=name, server_name=server_name, **kwargs
    )
    if response:
        ret["result"] = True
        ret["comment"] = f"Volume {name} was created"
        ret["changes"] = {"old": volumes[name], "new": response}
    else:
        ret["result"] = False
        ret["comment"] = f"Volume {name} failed to detach."
    return ret
