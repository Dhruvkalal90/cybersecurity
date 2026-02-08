from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.index,name="index",),
    path('signup/',views.signup_view,name="signup"),
    path('pnp/',views.pnp,name="pnp"),
    path('login/',views.login_view,name='login'),
    path('check-username/', views.check_username, name='check_username'),
    path('hacker-profile-form/',views.hacker_profile_form,name="hacker-profile-form"),
    path('business-profile-form/',views.business_profile_form,name='business-profile-form'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard',views.dashboard,name="dashboard"),
    path('booksession/',views.book_session,name="booksession"),
    path("pay-session/", views.pay_awareness_session, name="pay_session"),
    path("payment-success/", views.payment_success, name="payment_success"),

    path('blog_mgmt/',views.blog_mgmt_view,name="blog_mgmt"),
    path('blog_list',views.blog_list,name="blog_list"),
    path("blog/<int:blog_id>/",views.read_blog,name="read_blog"),
    path("blog_mgmt/edit/<int:blog_id>/", views.edit_blog, name="edit_blog"),
    path("blog_mgmt/delete/<int:blog_id>/", views.delete_blog, name="delete_blog"),
    path("awareness_session_list",views.awareness_session_list,name="awareness_session_list"),
    path("submit_complaint",views.submit_complaint,name="submit_complaint"),
    path("business_complaint_list",views.business_complaint_list,name="business_complaint_list"),
    path("hacker_apply_complaint",views.hacker_apply_complaint,name="hacker_apply_complaint"),
    path("apply-to-complaint/<int:complaint_id>/",views.apply_to_complaint,name="apply_to_complaint"),
    path("profile",views.profile,name="profile"),
    path("mywork",views.mywork,name="mywork"),
    path("hacker/complete-complaint/<int:complaint_id>/",views.complete_complaint,name="complete_complaint"),
    path("pay-complaint/", views.pay_complaint, name="pay_complaint"),
    path("complaint-payment-success/", views.complaint_payment_success, name="complaint_payment_success"),
    path("my_earnings/",views.my_earnings,name="my_earnings"),



    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)