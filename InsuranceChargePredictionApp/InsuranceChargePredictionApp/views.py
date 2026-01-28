from django.http import HttpResponse
from django.template import loader
from django.views.generic import TemplateView

class HomePageView(TemplateView):
    template_name = "home.html"
