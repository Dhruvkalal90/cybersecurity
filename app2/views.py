from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from app1.models import User, Role, Admin_Profile
from django.contrib.auth.decorators import login_required

def admin_login_view(request):
    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        # Basic validation
        if not email or not password:
            messages.error(request, "Enter email and password.")
            return redirect("login")

        # Authenticate
        user = authenticate(request, username=email, password=password)

        if user is None:
            messages.error(request, "Invalid admin credentials.")
            return redirect("login")

        # Check if role is ADMIN
        if not user.role or user.role.name.upper() != "ADMIN":
            messages.error(request, "Access denied. Admins only.")
            return redirect("login")

        # Login and redirect to admin dashboard
        login(request, user)
        return redirect("admin_dashboard")

    return render(request, "login.html")   # Same template

@login_required(login_url='/Root/admin_login')
def admin_dashboard(request):
    total_users = User.objects.count()
    context={
        "total_users":total_users
    }
    return render(request,"admin-dashboard.html",context)

@login_required(login_url='/Root/')
def admin_logout_view(request):
    logout(request)
    return redirect("admin_login")

