# -*- coding: utf-8 -*-
import re
from urlparse import urljoin, urlparse

from django.conf import settings
from mama_cas.models import ServiceTicket
from mama_cas.utils import add_query_params


VALID_SERVICES = getattr(settings, 'MAMA_CAS_VALID_SERVICES', ())
VALID_SERVICES_RE = [re.compile(s) for s in VALID_SERVICES]


def get_always_trusted_origins():
    return list(urlparse(service).netloc.replace('.', '\.') for service in VALID_SERVICES)


def get_service(url):
    """
    :param url: service url
    :return: the service which `url` belong to
    """
    if not url:
        return
    for i, service in enumerate(VALID_SERVICES_RE):
        if service.match(url):
            return VALID_SERVICES[i]


def get_service_urls(exclude_url):
    """
    :param exclude_url: service url excluded
    :return: MAMA_CAS_VALID_SERVICES login urls with ticket exclude `exclude_url`
    """
    exclude = get_service(exclude_url)
    return list(service for service in settings.MAMA_CAS_VALID_SERVICES if service != exclude)


def get_service_login_urls_with_ticket(exclude_url, user):
    """
    :param exclude_url: service url excluded
    :param user: generate `ServiceTicket` for `user`
    :return: MAMA_CAS_VALID_SERVICES login urls with ticket exclude `exclude_url`
    """
    urls = []
    for service in get_service_urls(exclude_url):
        st = ServiceTicket.objects.create_ticket(service=service,
                                                 user=user)
        url = urljoin(service, '/accounts/login/')
        urls.append(add_query_params(url, params={'ticket': st.ticket}))
    return urls
