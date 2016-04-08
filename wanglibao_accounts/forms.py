# -*- coding: utf-8 -*-
# from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth import authenticate
from mama_cas.forms import LoginForm


class LoginAuthenticationNoCaptchaForm(LoginForm):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    phone/password to login.
    """
    identifier = forms.CharField(label="phone", max_length=254, error_messages={'required': u'请输入手机号'})
    password = forms.CharField(label="Password", widget=forms.PasswordInput, error_messages={'required': u'请输入密码'})
    # captcha = CaptchaField(error_messages={'invalid': u'验证码错误', 'required': u'请输入验证码'})

    error_messages = {
        'invalid_login': u"用户名或者密码不正确",
        'frozen': u"用户账户已被冻结",
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super(LoginAuthenticationNoCaptchaForm, self).__init__(*args, **kwargs)

        self._errors = None

    def clean(self):
        identifier = self.cleaned_data.get('identifier')
        password = self.cleaned_data.get('password')

        if identifier and password:
            self.user_cache = authenticate(identifier=identifier, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'identifier': identifier},
                )
            else:
                if self.user_cache.sso_user.frozen:
                    raise forms.ValidationError(
                        self.error_messages['frozen'],
                        code='frozen',
                        params={'identifier': identifier},
                    )

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache
