from authtools.views import LoginView
from django.urls.base import reverse_lazy
from django.views.generic.base import RedirectView

from dashboard.forms import LoginForm


class DashboardRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):

        if self.request.user.is_superuser:
            return reverse_lazy('admin:index')
        return reverse_lazy('dashboard:course_list')


class CustomLoginView(LoginView):
    template_name = 'dashboard/login.html'
    form_class = LoginForm


