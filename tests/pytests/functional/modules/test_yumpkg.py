import pytest

import salt.modules.cmdmod
import salt.modules.pkg_resource
import salt.modules.yumpkg
import salt.utils.pkg.rpm


@pytest.fixture
def configure_loader_modules(minion_opts, grains):
    grains.update({"osarch": salt.utils.pkg.rpm.get_osarch()})
    return {
        pkg_resource: {
            "__grains__": grains,
        },
        yumpkg: {
            "__salt__": {
                "cmd.run": salt.modules.cmd.run,
                "cmd.run_all": salt.modules.cmd.run_all,
                "cmd.run_stdout": salt.modules.cmd.run_stdout,
                "pkg_resource.add_pkg": salt.modules.pkg_resource.add_pkg,
                "pkg_resource.parse_targets": salt.modules.pkg_resource.parse_targets,
            },
            "__opts__": minion_opts,
            "__grains__": grains,
        },
    }


@pytest.mark.slow_test
def test_yum_list_pkgs(grains):
    """
    compare the output of rpm -qa vs the return of yumpkg.list_pkgs,
    make sure that any changes to ympkg.list_pkgs still returns.
    """
    if grains["os_family"] != "RedHat":
        pytest.skip("Skip if not RedHat")
    cmd = [
        "rpm",
        "-qa",
        "--queryformat",
        "%{NAME}\n",
    ]
    known_pkgs = salt.modules.cmdmod.run(cmd, python_shell=False)
    listed_pkgs = salt.modules.yumpkg.list_pkgs()
    for line in known_pkgs.splitlines():
        assert any(line in d for d in listed_pkgs)


@pytest.mark.destructive_test
@pytest.mark.skip_if_not_root
def test_yumpkg_remove_wildcard():
    salt.modules.yumpkg.install(pkgs=["nginx-doc", "nginx-light"])
    ret = salt.modules.yumpkg.remove(name="nginx-*")
    assert not ret["nginx-light"]["new"]
    assert ret["nginx-light"]["old"]
    assert not ret["nginx-doc"]["new"]
    assert ret["nginx-doc"]["old"]