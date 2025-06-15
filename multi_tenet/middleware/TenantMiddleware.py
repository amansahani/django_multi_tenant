import psycopg2
from psycopg2 import pool
from django.conf import settings
from django.http import JsonResponse
from django.http.request import HttpRequest
from django.http.response import HttpResponse
import threading

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.connection_pools = {}
        self.lock = threading.Lock()
        self._initialize_pools()

    def _initialize_pools(self):
        for tenant_id, db_config in settings.TENANT_DATABASES.items():
            try:
                self.connection_pools[tenant_id] = psycopg2.connect(
                    1,20,
                    database = db_config['NAME'],
                    user=db_config['USER'],
                    password=db_config["PASSWORD"],
                    host=db_config["HOST"],
                    port=db_config["PORT"]
                )
            except Exception as e:
                print(e)
    def __call__(self, request: HttpRequest):
        tenant_id = request.headers.get('x-org', 'tenant1')

        if tenant_id not in self.connection_pools:
            return JsonResponse({
                'error': "Invalid tenant"
            })
        request.tenant_id = tenant_id
        request.db_pool = self.connection_pools[tenant_id]
        return self.get_response(request)