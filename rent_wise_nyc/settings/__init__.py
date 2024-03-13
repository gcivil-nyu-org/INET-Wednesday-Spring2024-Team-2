from .base import *
import os

if os.environ.get("ENV_NAME") == "prod":
    from .prod import *
elif os.environ.get("ENV_NAME") == "develop":
    from .develop import *
else:
    from .local import *
