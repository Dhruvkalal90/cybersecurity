from . import views
from django.urls import path

urlpatterns = [
    path('admin_login',views.admin_login_view,name="admin_login"),
    path("",views.admin_dashboard,name="admin_dashboard"),
    path("admin_logout/", views.admin_logout_view, name="admin_logout"),
    path("manage_users/",views.admin_manage_users,name="manage_users"),
    path("Manage_users/<int:user_id>/", views.admin_view_user, name="admin_view_user"),
    path("manage_users/<int:user_id>/delete/", views.admin_delete_user, name="admin_delete_user"),
    path("manage_payment/",views.manage_payment,name="manage_payment"),
    path("manage_content/",views.manage_content,name="manage_content"),
    path("blog/<int:blog_id>/", views.admin_read_blog, name="admin_view_post"),
    path("manage_content/<int:blog_id>/delete/", views.admin_delete_post, name="admin_delete_post"),
    path("admin_hacker_payout/<int:complaint_id>/",views.admin_hacker_payout,name="admin_hacker_payout"),
]
