from django.shortcuts import render

from .forms import CaseDesignerForm
from .services import evaluate_chain, format_expression, generate_vba


def designer(request):
    """Визуальный конструктор цепочки функций и генератор VBA-кода."""
    form = CaseDesignerForm(request.POST or None)
    context = {"form": form}
    if request.method == "POST" and form.is_valid():
        chain = form.cleaned_data["chain"]
        x_value = form.cleaned_data["x_value"]
        context.update(
            {
                "chain": chain,
                "expression": format_expression(chain),
                "result": evaluate_chain(x_value, chain),
                "vba_code": generate_vba(chain),
            }
        )
    return render(request, "case_builder/designer.html", context)
