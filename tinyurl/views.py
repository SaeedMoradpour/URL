from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from tinyurl.models import Url
from .lib.tiny import UrlHandler
from . import forms
import time


## display help

def index(request):
    "Render a simple help page"
    return HttpResponse("""
            <p> Usage example, copy paste examples in your browswer window and experiment: 
            <p> Shorten      ==> <a href=http://{0}/shortner/maketiny/www.pyramidcare.com.au.com>http://{0}/shortner/maketiny/www.pyramidcare.com.au</a>
            <p> Original Url ==> <a href=http://{0}/02a4e1/>http://{0}/02a4e1</a>

            """.format(request.get_host(), request.get_port())
                        )


# Create your views here.
@login_required(login_url='home')
def url_detail_view(request):
    url = Url.objects.get(id=1)
    context = {'originalurl': url.originalurl, 'tinyurl': url.shorturl}
    return render(request, "tinyurl/detail.html", context)


ORIGINAL_URL = 'originalurl'
TINY_URL = 'tinyurl'


## make tiny url
@login_required(login_url='home')
def make_tiny(request):
    form = forms.SuggestUrl()
    if request.method == 'POST':
        form = forms.SuggestUrl(request.POST)
        if form.is_valid():
            url = form.cleaned_data.get('o_url')
            suggested_url = form.cleaned_data.get('suggest_url')

            tinyurl = UrlHandler.get_tinyurl(request.user, url, suggested_url)
        #return redirect('tinyurl/maketiny.json',originalurl=url, tinyurl=tinyurl)
        context = {'originalurl':url, 'tinyurl': tinyurl}
        return render(request, "tinyurl/maketiny.json", context)

    return render(request, 'tinyurl/OtT.html', {'form': form})



## given the url code return tinyurl
def get_original(request, tinycode=None):
    context = {}
    context[TINY_URL] = ''
    context[ORIGINAL_URL] = ''

    if tinycode:
        tinyurl = get_full_url(request, tinycode)
        if tinycode:
            context[TINY_URL] = tinyurl if tinyurl else ''
            original_url = UrlHandler.get_originalurl(request, tinycode)
            context[ORIGINAL_URL] = original_url if original_url else ''
        else:
            print("Invalid url code")
    else:
        print("Missing url code")

    return render(request, "tinyurl/geturl.json", context)


def get_full_url(request, path):
    return request.scheme + "://" + request.get_host() + "/" + path


def get_param_from_request(request, key):
    print("getParamFromRequest. GET = {} \n POST {} \n".format(request.GET, request.POST))

    ret = None
    if key in request.GET:
        ret = request.GET[key]
    else:
        if key in request.POST:
            ret = request.POST[key]

    return ret
