from django.views.generic import TemplateView, FormView
from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect

from .forms import URLForm

from common import testing


class FormView(FormView):
    """ Form View """
    template_name = 'form.html'
    form_class = URLForm
    success_url = 'success'

    def form_valid(self, form):
        """ called when valid form data is POSTed """
        # set session values
        self.request.session['form-submitted'] = True
        self.request.session['url'] = form.cleaned_data['url']
        return HttpResponseRedirect(reverse(self.success_url))


class SuccessView(TemplateView):
    """ Success View """
    template_name = 'success.html'

    def get(self, request):
        """ main logic for when success view is called (GET) """
        if not request.session.get('form-submitted', False):
            print('unsuccessful')
            # return back to form
            return HttpResponseRedirect('/')
        else:
            # request session
            # this prevents from being called multiple times!
            request.session['form-submitted'] = False
            url = request.session.get('url')

            # get category name from testing module
            cat_name = testing.output_to_site_nb(url)
            if not cat_name:
                # when category name is None, change it to Undefined
                # should not go in here anyway...
                cat_name = 'Undefined'

            # go to success view
            context = {'category': cat_name}
            return render(request, self.template_name, context)
