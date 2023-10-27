from django.shortcuts import render

# trans = {"yes": "qui", "no": "noi", "portal": "portal", "Search": "Search"}


def index(request):
    context = {}
    context["trans"] = {
        "yes": "qui",
        "no": "noi",
        "portal": "portal",
        "Search": "Search",
    }
    # context["test"] = "hello"
    return render(request, "app/index.html", context)
