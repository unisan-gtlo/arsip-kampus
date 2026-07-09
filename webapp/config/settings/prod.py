from .base import *  # noqa: F401,F403

DEBUG = False
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["arsip.unisna-g.id"])  # noqa: F405

CSRF_TRUSTED_ORIGINS = [f"https://{h}" for h in ALLOWED_HOSTS] + [
    f"http://{h}" for h in ALLOWED_HOSTS
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)  # noqa: F405
