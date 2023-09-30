import enum
from typing import Optional

class permission(enum.Enum):
    MAINTAINER = 0
    ADMIN = 1

class Command():
    method: callable
    description: str
    keep_args: bool
    permissions: list[permission]
    aliases: list[str]
    pre_hook: Optional[callable]
    post_hook: Optional[callable]

    def __init__(
        self,
        method: callable,
        description: str = "",
        keep_args: bool = False,
        permissions: list[permission] = [],
        aliases: list[str] = [],
        pre_hook: Optional[callable] = None,
        post_hook: Optional[callable] = None
    ) -> None:
        self.method = method
        self.description = description
        self.keep_args = keep_args
        self.permissions = permissions
        self.aliases = aliases
        self.pre_hook = pre_hook
        self.post_hook = post_hook

    