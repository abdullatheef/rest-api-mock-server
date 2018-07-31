# -*- coding: utf-8 -*-
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer

from mock_api import callbacks
from mock_api.authentication import MockNoAuthentication
from mock_api import http_utils
from mock_api.models import ApiEndpoint
from mock_api.response_rules.errors import MatchingResponseNotFound
from mock_api.response_rules.resolvers import ResponseResolver


logger = logging.getLogger(__name__)


class MockApiView(APIView):
    authentication_classes = (MockNoAuthentication,)
    response_resolver_class = ResponseResolver
    api_endpoint = None
    renderer_classes = (JSONRenderer, )

    def get(self, request):
        try:
            logger.debug("Processing request %s %s", request.method, request.path_info)

            self.api_endpoint = ApiEndpoint.objects.get(path=request.path_info, method=request.method)
            logger.debug("Found api endpoint %s", self.api_endpoint)

            response = self.response_resolver_class(self.api_endpoint).resolve(request)
            logger.debug("Found response %s", response)

            callbacks.run_api_endpoint_callbacks(self.api_endpoint)

            return Response(status=response.status_code, data=response.get_content())
        except (ApiEndpoint.DoesNotExist, MatchingResponseNotFound):
            logger.error("No api endpoint found for %s %s", request.method, request.path_info)
            return Response(data={"message": "URL not found"}, status=status.HTTP_404_NOT_FOUND)

    post = get
    patch = get
    delete = get
    put = get
    options = get
