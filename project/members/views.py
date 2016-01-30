# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views import generic
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _
from .models import MembershipApplication
from .forms import ApplicationForm, ApplicationsApproveForm


class ApplyView(generic.CreateView):
    model = MembershipApplication
    template_name = "members/application_form.html"
    form_class = ApplicationForm

    def get_success_url(self):
        return reverse('members-application_received')


class ApplicationReceivedView(generic.TemplateView):
    template_name = "members/application_received.html"


class HomeView(generic.base.RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        return reverse('members-apply')


class AdminApplicationApproveView(generic.FormView):
    form_class = ApplicationsApproveForm
    template_name = "members/admin/approve_applications.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.kwargs['context'])
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        # Do stuff
        return self.render_to_response(context)


class AdminApplicationApproveMixin(object):
    view_class = AdminApplicationApproveView

    def get_urls(self):
        """Returns the additional urls used by the uploader."""
        urls = super().get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        info = opts.app_label, opts.model_name,
        my_urls = [
            url("^approve/$", admin_site.admin_view(self.approve_view), name='%s_%s_approve' % info),
        ]
        return my_urls + urls


    def approve_view(self, request, extra_context=None):
        """Displays a form that can upload transactions form a Nordea "NDA" transaction file."""
        # The revisionform view will check for change permission (via changeform_view),
        # but we also need to check for add permissions here.
        if not self.has_add_permission(request):  # pragma: no cover
            raise PermissionDenied
        model = self.model
        opts = model._meta
        try:
            each_context = self.admin_site.each_context(request)
        except TypeError:  # Django <= 1.7 pragma: no cover
            each_context = self.admin_site.each_context()
        # Get the rest of the context.
        context = dict(
            each_context,
            opts = opts,
            app_label = opts.app_label,
            module_name = capfirst(opts.verbose_name),
            title = _("Approve selected applications"),
        )
        context.update(extra_context or {})
        view = self.view_class.as_view()

        return view(request, context=context)
