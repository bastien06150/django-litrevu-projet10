from django.shortcuts import render
from django.http import HttpResponse

...
from listings.models import Band
from listings.models import Title

...


def hello(request):
    bands = Band.objects.all()
    return render(request, "listings/hello.html", {"bands": bands})


def about(request):
    return HttpResponse("<h1>A propos</h1> <p>Nous adorons merch !</p>")


def listings(request):
    title = Title.objects.all()
    return HttpResponse(
        f"""
        <h1>Listings</h1> 
        <p>Voici le listing !</p>
        <ul>
            <li>{title[0].name}</li>
            <li>{title[1].name}</li>
            <li>{title[2].name}</li>
        <ul>
"""
    )


def contact(request):
    return HttpResponse(
        "<h1>Contactez Nous</h1> <p>Vous pouvez nous contactez sur instagram !</p>"
    )
