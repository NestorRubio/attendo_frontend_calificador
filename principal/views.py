from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render


def index(request):
    '''
    template = loader.get_template('partials/base.html')
    context = {'Nada':0}
    HttpResponse(template.render(context, request))  #

    '''

    return render(request,'partials/base.html')