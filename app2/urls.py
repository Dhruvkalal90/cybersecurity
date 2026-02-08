from . import views
from django.urls import path

urlpatterns = [
    path('admin_login',views.admin_login_view,name="admin_login"),
    path("",views.admin_dashboard,name="admin_dashboard"),
    path("admin_logout/", views.admin_logout_view, name="admin_logout"),
    path("manage_users/",views.admin_manage_users,name="manage_users"),
    path("Manage_users/<int:user_id>/", views.admin_view_user, name="admin_view_user"),
    path("manage_users/<int:user_id>/delete/", views.admin_delete_user, name="admin_delete_user"),
]
