from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns(
	'',
	url(r'^dashboard/', views.dashboard, name='dashboard')
)
