from .base import *  # noqa: <F403>
import os

if os.environ.get("ENV_NAME") == "prod":
    from .prod import *  # noqa: <F403>
elif os.environ.get("ENV_NAME") == "develop":
    from .develop import *  # noqa: <F403>
else:
    from .local import *  # noqa: <F403>
