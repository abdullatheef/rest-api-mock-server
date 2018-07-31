from django.contrib.auth.models import User
u, _ = User.objects.get_or_create(username="dj")
u.is_superuser = True
u.is_staff  = True
u.save()


class Middleware(object):
    def process_request(self, request):
        request.user = User.objects.filter()[0]