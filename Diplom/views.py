from django.shortcuts import render
from django.http import HttpResponseRedirect

def toindex(request):
    return HttpResponseRedirect("/PlaningSystem/index")