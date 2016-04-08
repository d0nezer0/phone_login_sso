# -*- coding: utf-8 -*-
import logging

from django.conf import settings

from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth import login
from django.utils.translation import ugettext_lazy as _

from mama_cas.utils import add_query_params, to_bool
from mama_cas.models import ServiceTicket
from mama_cas.utils import is_valid_service_url, redirect
from mama_cas.views import LoginView, LogoutView

from wanglibao_accounts.forms import LoginAuthenticationNoCaptchaForm
from wanglibao_sso.utils import get_service_login_urls_with_ticket, get_service_urls, get_always_trusted_origins


logger = logging.getLogger(__name__)


def provider(request):
    return render(request, 'provider.html', {
        'debug': settings.DEBUG,
        'always_trusted_origins': get_always_trusted_origins()
    })


# class CustomLoginView(JSONResponseMixin, LoginView):
class CustomLoginView(LoginView):

    template_name = 'login.html'
    form_class = LoginAuthenticationNoCaptchaForm

    def get(self, request, *args, **kwargs):
        """
        (2.1) As a credential requestor, /login accepts three optional
        parameters:

        1. ``service``: the identifier of the application the client is
           accessing. We assume this identifier to be a URL.
        2. ``renew``: requires a client to present credentials
           regardless of any existing single sign-on session.
        3. ``gateway``: causes the client to not be prompted for
           credentials. If a single sign-on session exists the user
           will be logged in and forwarded to the specified service.
           Otherwise, the user remains logged out and is forwarded to
           the specified service.
        """
        service = request.GET.get('service')
        renew = to_bool(request.GET.get('renew'))
        gateway = to_bool(request.GET.get('gateway'))

        if renew:
            logger.debug("Renew request received by credential requestor")
        elif gateway and service:
            logger.debug("Gateway request received by credential requestor")
            if request.user.is_authenticated():
                st = ServiceTicket.objects.create_ticket(service=service,
                                                         user=request.user)
                if self.warn_user():
                    return redirect('cas_warn', params={'service': service,
                                                        'ticket': st.ticket})
                return redirect(service, params={'ticket': st.ticket})
            else:
                params = request.GET.copy()
                params.pop('service', None)
                params.pop('renew', None)
                return redirect(service, params=params)
        elif request.user.is_authenticated():
            if service:
                logger.debug("Service ticket request received "
                             "by credential requestor")
                st = ServiceTicket.objects.create_ticket(service=service,
                                                         user=request.user)
                if self.warn_user():
                    return redirect('cas_warn', params={'service': service,
                                                        'ticket': st.ticket})
                return redirect(service, params={'ticket': st.ticket})
            else:
                msg = _("You are logged in as %s") % request.user
                messages.success(request, msg)
        return super(CustomLoginView, self).get(request, *args, **kwargs)

    def form_invalid(self, form):
        login(self.request, form.user_cache)
        fmt = self.request.REQUEST.get('format', None)
        if fmt in ('json', ):
            return self.render_json_response(self.invalid_response(form))
        return super(CustomLoginView, self).form_invalid(form)

    def form_valid(self, form):
        fmt = self.request.REQUEST.get('format', None)
        if fmt in ('json', ):
            return self.render_json_response(self.valid_response(form))
        return super(CustomLoginView, self).form_valid(form)

    def invalid_response(self, form):
        data = dict(state=False, error=u"用户名或密码错误")
        return data

    def valid_response(self, form):

        login(self.request, form.user)
        logger.info("Single sign-on session started for %s" % form.user)

        if form.cleaned_data.get('warn'):
            self.request.session['warn'] = True

        service = self.request.REQUEST.get('service')
        if service:
            st = ServiceTicket.objects.create_ticket(service=service,
                                                     user=self.request.user,
                                                     primary=True)
            if not is_valid_service_url(service):
                data = dict(state=False, error=u'permission denied')
            else:
                cross_domain_urls = get_service_login_urls_with_ticket(service, self.request.user)
                params = {'ticket': st.ticket}
                next_page = self.request.REQUEST.get('next', '')
                if next_page and is_valid_service_url(next_page):
                    params['next'] = next_page
                redirect_to = add_query_params(service, params=params)
                data = dict(state=True, redirect_to=redirect_to, cross_domain_urls=cross_domain_urls)
        else:
            data = dict(state=False)
        return data


class CustomLogoutView(LogoutView):
    """
    (2.3) End a client's single sign-on session.

    Accessing this view ends an existing single sign-on session,
    requiring a new single sign-on session to be established for
    future authentication attempts.

    [CAS 3.0] If ``service`` is specified and
    ``MAMA_CAS_FOLLOW_LOGOUT_URL`` is ``True``, the client will be
    redirected to the specified service URL.

    [CAS 1.0, CAS 2.0] If ``url`` is specified, by default it will be
    displayed to the user as a recommended link to follow. This
    behavior can be altered by setting ``MAMA_CAS_FOLLOW_LOGOUT_URL``
    to ``True``, which redirects the client to the specified URL.
    """
    def get(self, request, *args, **kwargs):
        service = request.GET.get('service')
        url = request.GET.get('url')
        follow_url = getattr(settings, 'MAMA_CAS_FOLLOW_LOGOUT_URL', True)
        self.logout_user(request)

        if service and follow_url:
            return redirect(service)

        elif url and is_valid_service_url(url):
            if follow_url:
                return redirect(url)
            msg = _("The application provided this link to follow: %s") % url
            messages.success(request, msg)

        return redirect('login_view')


class UserInfo(LoginView):
    """
    (2.3) End a client's single sign-on session.

    Accessing this view ends an existing single sign-on session,
    requiring a new single sign-on session to be established for
    future authentication attempts.

    [CAS 3.0] If ``service`` is specified and
    ``MAMA_CAS_FOLLOW_LOGOUT_URL`` is ``True``, the client will be
    redirected to the specified service URL.

    [CAS 1.0, CAS 2.0] If ``url`` is specified, by default it will be
    displayed to the user as a recommended link to follow. This
    behavior can be altered by setting ``MAMA_CAS_FOLLOW_LOGOUT_URL``
    to ``True``, which redirects the client to the specified URL.
    """
    def get(self, request, *args, **kwargs):

        user = request.user

        return {'user': user}
