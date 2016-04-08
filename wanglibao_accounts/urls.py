from django.conf.urls import patterns, url

from views import CustomLoginView, CustomLogoutView, UserInfo

urlpatterns = patterns(
    '',
    url(r'^login/$', CustomLoginView.as_view(), name='login_view'),
    url(r'^logout/?$', CustomLogoutView.as_view(), name='logout_view'),
    url(r'^user/?$', UserInfo.as_view(), name='logout_view'),
)
