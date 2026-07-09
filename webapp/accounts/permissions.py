from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


def _has_role(user, roles):
    return user.is_authenticated and user.role in roles


def role_required(*roles):
    """Decorator for function-based views: anonymous users are redirected to
    login; authenticated users with the wrong role get a 403 (matching the
    behaviour of RoleRequiredMixin for class-based views)."""

    def decorator(view_func):
        @login_required(login_url="accounts:login")
        def wrapped(request, *args, **kwargs):
            if not _has_role(request.user, roles):
                raise PermissionDenied("Anda tidak memiliki akses ke halaman ini.")
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin for class-based views: require login + one of `allowed_roles`.
    Anonymous users are redirected to login; authenticated users with the
    wrong role get a 403 (Django's default UserPassesTestMixin behaviour)."""

    allowed_roles = ()
    login_url = "accounts:login"

    def test_func(self):
        return _has_role(self.request.user, self.allowed_roles)
