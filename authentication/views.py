from django.urls import reverse_lazy
from .forms import SignUpForm
from django.views.generic.edit import CreateView
from django.contrib.auth import logout


class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('index')
    template_name = 'registration/signup.html'
