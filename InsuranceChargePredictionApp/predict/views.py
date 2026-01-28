from django.urls import reverse_lazy
from .forms import PredictionForm
from django.views.generic import FormView

print(f"PredictionForm importé : {PredictionForm}")

class PredictionView(FormView):
    form_class = PredictionForm
    template_name = 'predict/prediction.html'
    success_url = reverse_lazy('prediction')

    def form_valid(self, form):
        return super().form_valid(form)
