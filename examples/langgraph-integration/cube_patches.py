# Copyright (c) 2026 Tencent Inc.
# SPDX-License-Identifier: Apache-2.0

"""CubeSandbox envd compatibility patches for the E2B Python SDK.

Cube envd only supports the ``root`` user, and older envd builds reject the
``stdin`` keyword on ``commands.run()``. Apply these patches before creating
sandboxes or importing langchain-e2b backends.
"""

from __future__ import annotations

import functools
import inspect
from typing import Any, Callable

_PATCHED = False


def _patch_filesystem(fs_cls: type) -> None:
    for name in (
        "read",
        "write",
        "write_files",
        "list",
        "exists",
        "get_info",
        "remove",
        "rename",
        "make_dir",
        "watch_dir",
    ):
        original = getattr(fs_cls, name, None)
        if original is None:
            continue

        params = list(inspect.signature(original).parameters.keys())
        user_pos = params.index("user") - 1 if "user" in params else None

        def _make(fn: Callable[..., Any], user_index: int | None = user_pos) -> Callable[..., Any]:
            @functools.wraps(fn)
            def _wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
                if user_index is not None and len(args) > user_index:
                    args_list = list(args)
                    if args_list[user_index] is None:
                        args_list[user_index] = "root"
                    args = tuple(args_list)
                else:
                    kwargs.setdefault("user", "root")
                return fn(self, *args, **kwargs)

            return _wrapper

        setattr(fs_cls, name, _make(original))


def _patch_commands(cmd_cls: type) -> None:
    original_run = cmd_cls.run

    @functools.wraps(original_run)
    def _patched_run(self: Any, *args: Any, **kwargs: Any) -> Any:
        if hasattr(self, "_envd_version"):
            from e2b.sandbox_sync.commands.command import ENVD_COMMANDS_STDIN

            if self._envd_version < ENVD_COMMANDS_STDIN:
                kwargs.pop("stdin", None)
        return original_run(self, *args, **kwargs)

    cmd_cls.run = _patched_run


def apply_cube_envd_patches() -> None:
    """Patch sync E2B SDK classes for CubeSandbox envd."""
    global _PATCHED
    if _PATCHED:
        return

    import e2b.envd.rpc as e2b_rpc
    from e2b.sandbox_sync.commands.command import Commands as SyncCommands
    from e2b.sandbox_sync.filesystem.filesystem import Filesystem as SyncFilesystem

    e2b_rpc.default_username = "root"
    _patch_filesystem(SyncFilesystem)
    _patch_commands(SyncCommands)
    _PATCHED = True
