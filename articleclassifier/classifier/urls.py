from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.FormView.as_view(), name='form'),
    url('success/', views.SuccessView.as_view(), name='success'),
]
