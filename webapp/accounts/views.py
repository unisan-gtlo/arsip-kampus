from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, View
from django.shortcuts import get_object_or_404, redirect

from .forms import LoginForm, UserCreateForm
from .models import User
from .permissions import RoleRequiredMixin


class AccountsLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["show_sidebar"] = False
        return context


class AccountsLogoutView(LogoutView):
    next_page = "accounts:login"


class UserListView(RoleRequiredMixin, ListView):
    allowed_roles = (User.Role.ADMIN,)
    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "users"

    def get_queryset(self):
        return User.objects.all().order_by("username")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = UserCreateForm()
        return context


class UserCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = (User.Role.ADMIN,)
    model = User
    form_class = UserCreateForm
    success_url = reverse_lazy("accounts:user_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"User '{self.object.username}' berhasil ditambahkan.")
        return response

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return redirect("accounts:user_list")


class UserDeleteView(RoleRequiredMixin, View):
    allowed_roles = (User.Role.ADMIN,)

    def post(self, request, pk):
        target = get_object_or_404(User, pk=pk)
        if target.pk == request.user.pk:
            messages.error(request, "Tidak dapat menghapus akun yang sedang aktif.")
        else:
            username = target.username
            target.delete()
            messages.success(request, f"User '{username}' berhasil dihapus.")
        return redirect("accounts:user_list")
