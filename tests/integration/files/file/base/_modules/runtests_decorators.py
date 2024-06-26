import logging
import os
import pathlib
import time

import salt.utils.decorators

log = logging.getLogger(__name__)

REPO_ROOT_DIR = pathlib.Path(os.environ["REPO_ROOT_DIR"]).resolve()
STATE_BASE_DIR = REPO_ROOT_DIR / "tests" / "integration" / "files" / "file" / "base"
EXIT_CODE_SH = STATE_BASE_DIR / "exit_code.sh"
EXIT_CODE_CMD = STATE_BASE_DIR / "exit_code.cmd"


def _exit_code(code):
    if os.name == "nt":
        cmd = f"cmd /c {EXIT_CODE_CMD} {code}"
    else:
        cmd = f"/usr/bin/env sh {EXIT_CODE_SH} {code}"
    return cmd


def _fallbackfunc():
    return False, "fallback"


def working_function():
    return True


@salt.utils.decorators.depends(True)
def booldependsTrue():
    return True


@salt.utils.decorators.depends(False)
def booldependsFalse():
    return True


@salt.utils.decorators.depends("time")
def depends():
    ret = {"ret": True, "time": time.time()}
    return ret


@salt.utils.decorators.depends("time123")
def missing_depends():
    return True


@salt.utils.decorators.depends("time", fallback_function=_fallbackfunc)
def depends_will_not_fallback():
    ret = {"ret": True, "time": time.time()}
    return ret


@salt.utils.decorators.depends("time123", fallback_function=_fallbackfunc)
def missing_depends_will_fallback():
    ret = {"ret": True, "time": time.time()}
    return ret


@salt.utils.decorators.depends(_exit_code(42), retcode=42)
def command_success_retcode():
    return True


@salt.utils.decorators.depends(_exit_code(42), retcode=0)
def command_failure_retcode():
    return True


@salt.utils.decorators.depends(_exit_code(42), nonzero_retcode=True)
def command_success_nonzero_retcode_true():
    return True


@salt.utils.decorators.depends(_exit_code(0), nonzero_retcode=True)
def command_failure_nonzero_retcode_true():
    return True


@salt.utils.decorators.depends(_exit_code(0), nonzero_retcode=False)
def command_success_nonzero_retcode_false():
    return True


@salt.utils.decorators.depends(_exit_code(42), nonzero_retcode=False)
def command_failure_nonzero_retcode_false():
    return True


# The 'depends_versioned.py'-module has __version__ = '1.8'
@salt.utils.decorators.depends("depends_versioned", version="1.0")
def version_depends_false():
    return True


@salt.utils.decorators.depends("depends_versioned", version="2.0")
def version_depends_true():
    return True


# The 'depends_versionless.py'-module does not have a `__version__`-string
@salt.utils.decorators.depends("depends_versionless", version="0.2")
def version_depends_versionless_true():
    return True
