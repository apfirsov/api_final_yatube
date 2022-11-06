from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """About author page view-class."""
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """About tech page view-class."""
    template_name = 'about/tech.html'
