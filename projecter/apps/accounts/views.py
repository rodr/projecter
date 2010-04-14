from django import http
from django.conf import settings
from django.template import RequestContext

from django.shortcuts import render_to_response, get_object_or_404
from django.contrib import messages

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm

from projecter.apps.accounts import forms

def common_login(request, template="accounts/login.html"):
    if request.user.is_authenticated():
        raise http.Http404()

    redirect_to = request.REQUEST.get('next', '/')
    if request.method == "POST":
        form = UserLogin(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())

            if request.session.test_cookie_worked():
              request.session.delete_test_cookie()

            return http.HttpResponseRedirect(redirect_to)
    else:
       form = forms.UserLogin(request)

    request.session.set_test_cookie()

    return render_to_response(template, RequestContext(request, {
        "form": form
    }))
    
@login_required
def common_logout(request):
    logout(request)

    messages.info(request, "Haz salido satisfactoriamente de la aplicacion.")

    return http.HttpResponseRedirect("/login/")
  
def common_404(request):
    return render_to_response('common/templates/404.html')
