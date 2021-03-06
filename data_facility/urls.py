''' URLS for DFAdmin '''
from django.conf.urls import include, url
from django.views.generic.base import RedirectView
from django.contrib import admin
from data_facility_admin.api import urls as admin_router
from data_facility_metadata.api import urls as metadata_router
#from rest_framework_swagger.views import get_swagger_view
from ajax_select import urls as ajax_select_urls
#from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view
#from rest_framework_swagger.renderers import OpenAPIRenderer
from graphene_django.views import GraphQLView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
import rest_framework
from django.conf import settings


class PrivateGraphQLView(LoginRequiredMixin, GraphQLView):
    """Adds a login requirement to graphQL API access via main endpoint."""
    pass

from graphene_django.views import GraphQLView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


class DRFAuthenticatedGraphQLView(GraphQLView):
    def parse_body(self, request):
        if isinstance(request, rest_framework.request.Request):
            return request.data
        return super(DRFAuthenticatedGraphQLView, self).parse_body(request)
    # custom view for using DRF TokenAuthentication with graphene GraphQL.as_view()
    # all requests to Graphql endpoint will require token for auth, obtained from DRF endpoint
    # https://github.com/graphql-python/graphene/issues/249
    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super(DRFAuthenticatedGraphQLView, cls).as_view(*args, **kwargs)
        view = permission_classes((IsAuthenticated,))(view)
        view = authentication_classes((JSONWebTokenAuthentication, TokenAuthentication,))(view)
        #view = authentication_classes((TokenAuthentication,))(view)
        view = api_view(['POST'])(view)
        return view


urlpatterns = [
    url(r'^grappelli/', include('grappelli.urls')),  # grappelli URLS
    url(r'^', admin.site.urls),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # url('^accounts/', admin.site.urls),

    # django-ajax-select
    url(r'^ajax_select/', include(ajax_select_urls)),
    url(r'^nested_admin/', include('nested_admin.urls')),
    url(r'^api/v1/graphqlapi', csrf_exempt(DRFAuthenticatedGraphQLView.as_view(graphiql=True))),
    url(r'^api/v1/graphql', PrivateGraphQLView.as_view(graphiql=True)),
]

# API
DFADMIN_API = 'DFAdmin API'

api_urls = admin_router.urls
api_urls += metadata_router.urls

urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^api/v1/', include(api_urls)),#,  namespace='api')),
#    url(r'^api/v1/schema.json$', get_schema_view(title=DFADMIN_API, renderer_classes=[OpenAPIRenderer]), name='api-schema'),
#    url(r'^api/v1/docs/swagger/$', get_swagger_view(title=DFADMIN_API), name='api-swagger'),
#    url(r'^api/v1/docs/open-api/', include_docs_urls(title=DFADMIN_API), name='api-docs'),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/images/favicon.ico')),
    url('^prometheus/', include('django_prometheus.urls')),
]

# Django Debug Toolbar config
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls)),]



# # Admin to work on /
# urlpatterns += [
#     url(r'^', admin.site.urls),
# ]
