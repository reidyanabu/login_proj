from django.urls import path, include

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('',include('login_app.urls'))
]
