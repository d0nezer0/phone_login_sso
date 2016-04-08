# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model

from wanglibao_accounts.utils import detect_identifier_type
from wanglibao_profile.models import WanglibaoUserProfile

User = get_user_model()


class EmailPhoneUsernameAuthBackend(object):

    def authenticate(self, **kwargs):
        identifier = None

        if 'identifier' in kwargs:
            identifier = kwargs['identifier']
        elif 'email' in kwargs:
            identifier = kwargs['email']
        elif 'username' in kwargs:
            identifier = kwargs['username']

        if not identifier:
            return None

        # TODO add a middleware for identifier_type detection and add it to the request
        identifier_type = detect_identifier_type(identifier)

        if identifier_type == 'email':
            # user_filter = Q(email=identifier)
            profile = WanglibaoUserProfile.objects.filter(email=identifier).first()

        elif identifier_type == 'phone':
            # user_filter = Q(wanglibaouserprofile__phone=identifier) & Q(wanglibaouserprofile__phone_verified=True)
            profile = WanglibaoUserProfile.objects.get(phone=identifier)

        else:
            profile = None

        users = User.objects.filter(id=profile.user.id)

        password = kwargs['password']

        # TODO fix the following logic, it made some assumptions, clean it and make it simple
        # The checking logic:
        # When there is one active user matched, then only check the active user
        # When no active user matched, then check each user to find the match.
        # The rational: Some bad user may use other people's email address but not able
        #    To activate it, to accomodate this situation, we provide a user the chance to
        #    login even if there are un active user with same email or phone number.
        # In the opposite, when there is one active user, then that user is THE correct user and
        #    all other users should be forbidden.
        #
        active_user = next((u for u in users if u.is_active), None)

        if active_user:
            if active_user.check_password(password):
                return active_user
            else:
                return None

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
