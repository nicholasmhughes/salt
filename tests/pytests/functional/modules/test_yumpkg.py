import pytest

import salt.modules.cmdmod as cmd
import salt.modules.pkg_resource as pkg_resource
import salt.modules.yumpkg as yumpkg


@pytest.fixture
def configure_loader_modules(minion_opts):
    return {
        yumpkg: {
            "__salt__": {
                "cmd.run_all": cmd.run_all,
                "cmd.run": cmd.run,
                "pkg_resource.parse_targets": pkg_resource.parse_targets,
            },
            "__opts__": minion_opts,
        },
    }


@pytest.mark.destructive_test
@pytest.mark.skip_if_not_root
def test_yumpkg_remove_wildcard():
    yumpkg.install(pkgs=["nginx-doc", "nginx-light"])
    ret = yumpkg.remove(name="nginx-*")
    assert not ret["nginx-light"]["new"]
    assert ret["nginx-light"]["old"]
    assert not ret["nginx-doc"]["new"]
    assert ret["nginx-doc"]["old"]
