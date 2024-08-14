from django.http import HttpResponse
from django.shortcuts import render
import pathlib
from visits.models import PageVisit

this_dir = pathlib.Path(__file__).resolve().parent

def home_view(request, *args, **kwargs):
    if request.user.is_authenticated:
        print(request.user)
    return about_view(request, *args, **kwargs)

def about_view(request, *args, **kwargs):
    qs = PageVisit.objects.all()
    page_qs = PageVisit.objects.filter(path=request.path)
    try:
        percent = (page_qs.count()*100.0)/qs.count()
    except:
        percent = 0
    my_title = "Django Page"
    html_template = "home.html"
    my_context = {
        "page_title" : my_title,
        "page_visit_count" : page_qs.count(),
        "percent" : percent,
        "total_visit_count" : qs.count()
    }
    PageVisit.objects.create(path= request.path)
    return render(request, html_template, my_context)

def my_old_home_page_view(request, *args, **kwargs):
    my_title = "My Django Page"
    my_context = {"page_title": my_title}
    # skipcq: PYL-C0209
    html_ = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
    </head>
    <body>
        <h1>{page_title}Hello Amigo</h1>
    </body>
    </html>
    """.format(**my_context)
    # html_file_path = this_dir / "home.html"
    # html_ = html_file_path.read_text()
    return HttpResponse(html_)