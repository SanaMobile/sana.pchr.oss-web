from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from sana_pchr import reporting
from sana_pchr.api import ProvisioningResource, CredentialsResource, SyncResource, SearchPatientResource, \
    SearchPhysicianResource, UpdateResource
from sana_pchr.settings import MEDIA_URL, MEDIA_ROOT, STATIC_ROOT, STATIC_URL

api_urlpatterns = patterns('',
                           url(r'^auth/provision', include(ProvisioningResource.urls())),
                           url(r'^auth/credentials', include(CredentialsResource.urls())),
                           url(r'^sync/', include(SyncResource.urls())),
                           url(r'^search/patient/', include(SearchPatientResource.urls())),
                           url(r'^search/physician/', include(SearchPhysicianResource.urls())),
                           url(r'^app/update/', include(UpdateResource.urls())),
                           )

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'sana_pchr.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),
                       url(r'^api/v1/', include(api_urlpatterns)),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^reporting/', include('sana_pchr.reporting.urls')),
                       url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'reporting/login.html' }),
                       ) + static(MEDIA_URL, document_root=MEDIA_ROOT) + static(STATIC_URL, document_root=STATIC_ROOT)
