from . import views
from django.urls import path

urlpatterns = [
    path('admin_login',views.admin_login_view,name="admin_login"),
    path("",views.admin_dashboard,name="admin_dashboard"),
    path("admin_logout/", views.admin_logout_view, name="admin_logout"),
]
