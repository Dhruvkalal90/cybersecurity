from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from app1.models import User, Role, Admin_Profile,Complaints,Payments,Hacker_Profile
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.db.models import F,Q
from django.core.paginator import Paginator

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

    # --- STAT COUNTS ---
    total_users = User.objects.count()
    total_complaints = Complaints.objects.count()

    active_hackers = Complaints.objects.filter(
        assigned_hacker__isnull=False
    ).values("assigned_hacker").distinct().count()

    total_revenue = Payments.objects.filter(
        status="Paid"
    ).aggregate(total=Sum("amount"))["total"] or 0

    pending_reviews = Complaints.objects.filter(
        status="Pending"
    ).count()

    # --- RECENT COMPLAINTS ---
    recent_complaints = Complaints.objects.select_related(
        "business"
    ).order_by("-date_submitted")[:5]

    # --- RECENT USERS ---
    recent_users = User.objects.select_related(
        "role"
    ).order_by("-date_created")[:5]

    context = {
        "total_users": total_users,
        "total_complaints": total_complaints,
        "active_hackers": active_hackers,
        "total_revenue": total_revenue,
        "pending_reviews": pending_reviews,
        "recent_complaints": recent_complaints,
        "recent_users": recent_users,
    }

    return render(request, "admin-dashboard.html", context)

@login_required(login_url='/Root/')
def admin_logout_view(request):
    logout(request)
    return redirect("admin_login")


@login_required
def admin_manage_users(request):

    # -------- GET FILTER VALUES --------
    user_type = request.GET.get("user_type", "")
    status = request.GET.get("status", "")
    search = request.GET.get("search", "")

    users = User.objects.select_related("role").order_by("-date_created")

    # -------- FILTER: USER TYPE --------
    if user_type:
        users = users.filter(role__name__iexact=user_type)

    # -------- FILTER: STATUS --------
    if status == "active":
        users = users.filter(is_active=True)
    elif status == "inactive":
        users = users.filter(is_active=False)

    # -------- FILTER: SEARCH --------
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search)
        )

    # -------- PAGINATION (10 PER PAGE) --------
    paginator = Paginator(users, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # -------- COUNTS FOR CARDS --------
    context = {
        "users": page_obj,
        "page_obj": page_obj,
        "total_users": User.objects.count(),
        "hacker_count": User.objects.filter(role__name="HACKER").count(),
        "business_count": User.objects.filter(role__name="BUSINESS").count(),
        "admin_count": User.objects.filter(role__name="ADMIN").count(),

        # preserve filters
        "selected_user_type": user_type,
        "selected_status": status,
        "search_query": search,
    }
    return render(request, "admin-manage-user.html", context)


@login_required(login_url='/Root/admin_login')
def admin_view_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, "user-detail.html", {"view_user": user})


@login_required(login_url='/Root/admin_login')
def admin_delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        user.delete()
        return redirect("manage_users")

    return redirect("manage_users")