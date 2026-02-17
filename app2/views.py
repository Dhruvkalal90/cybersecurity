from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from app1.models import User, Role, Admin_Profile,Complaints,Payments,Hacker_Profile,Blogs
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.db.models import F,Q
from django.core.paginator import Paginator
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from app1.models import Blogs,User,HackerPayout
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

    totalposts= Blogs.objects.count()

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
        "posts": totalposts,
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

@login_required(login_url='/Root/admin_login')
def manage_payment(request):

    # ==========================
    # 1. HACKER PAYABLES (UNPAID)
    # ==========================
    hacker_payables = HackerPayout.objects.select_related(
        "complaint",
        "hacker__user"
    ).filter(
        status="PENDING"
    ).order_by("-completed_on")

    # ==========================
    # 2. ALL TRANSACTIONS
    # ==========================
    all_transactions = Payments.objects.select_related(
        "payer",
        "receiver"
    ).order_by("-date")

    # ==========================
    # STATS (optional but useful)
    # ==========================

    return render(request, "admin-manage-payment.html", {
        "hacker_payables": hacker_payables,
        "all_transactions": all_transactions,
    })





@login_required(login_url='/Root/admin_login')
def manage_content(request):
    search = request.GET.get("search", "")

    posts = Blogs.objects.select_related("author", "author__role").order_by("-created_on")


    # -------- FILTER: SEARCH (TITLE / AUTHOR) --------
    if search:
        posts = posts.filter(
            Q(title__icontains=search) |
            Q(author__username__icontains=search) |
            Q(author__email__icontains=search)
        )

    # -------- STATS --------
    total_posts = posts.count()
    total_views = posts.aggregate(total=Sum("views"))["total"] or 0

    # -------- PAGINATION --------
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "posts": page_obj,
        "page_obj": page_obj,
        "total_posts": total_posts,
        "total_views": total_views,

        # preserve filters
        "search_query": search,
    }

    return render(request, "admin-manage-content.html", context)


@login_required(login_url='/Root/admin_login')
def admin_read_blog(request, blog_id):
    blog = get_object_or_404(Blogs, id=blog_id)

    session_key = f"viewed_blog_{blog_id}"

    # Only increment if this blog was not viewed in this session
    if not request.session.get(session_key, False):
        blog.views = F("views") + 1
        blog.save(update_fields=["views"])
        request.session[session_key] = True

    # To avoid race condition, refresh from DB
    blog.refresh_from_db()

    related = Blogs.objects.exclude(id=blog_id).order_by("-views")[:3]

    return render(request, "read-blog.html", {
        "blog": blog,
        "related": related
    })

@login_required(login_url='/Root/admin_login')
def admin_delete_post(request, blog_id):
    post = get_object_or_404(Blogs, id=blog_id)

    if request.method == "POST":
        post.delete()
        messages.success(request,"Post deleted")
        return redirect("manage_content")

    return redirect("manage_content")

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from app1.models import (
    Complaints,
    Applications,
    ComplaintCompletion,
    HackerPayout,
    Complaint_Status_History,
    Payments
)


@login_required
def admin_hacker_payout(request, complaint_id):

    if request.user.role.name != "ADMIN":
        return redirect("dashboard")

    complaint = get_object_or_404(
        Complaints.objects.select_related(
            "business__user",
            "assigned_hacker__user",
            "payment"
        ),
        id=complaint_id
    )

    # ==============================
    # HANDLE ACTIONS
    # ==============================
    if request.method == "POST":

        action = request.POST.get("action")

        # ------------------------------------------------
        # 1️⃣ MARK VERIFIED
        # ------------------------------------------------
        if action == "verify":

            if complaint.status != "Completed":
                messages.error(request, "Complaint must be completed first.")
                return redirect("admin_hacker_payout", complaint_id)

            old_status = complaint.status
            complaint.status = "Resolved"
            complaint.save()

            Complaint_Status_History.objects.create(
                complaint=complaint,
                old_status=old_status,
                new_status="Resolved",
                updated_by=request.user
            )

            messages.success(request, "Complaint marked as verified.")
            return redirect("admin_hacker_payout", complaint_id)

        # ------------------------------------------------
        # 2️⃣ REASSIGN
        # ------------------------------------------------
        if action == "reassign":

            if complaint.status == "Resolved":
                messages.error(request, "Cannot reassign a verified complaint.")
                return redirect("admin_hacker_payout", complaint_id)

            old_status = complaint.status

            with transaction.atomic():
                complaint.assigned_hacker = None
                complaint.status = "Pending"
                complaint.save()

                # Delete payout if exists
                HackerPayout.objects.filter(complaint=complaint).delete()

                Complaint_Status_History.objects.create(
                    complaint=complaint,
                    old_status=old_status,
                    new_status="Pending",
                    updated_by=request.user
                )

            messages.success(request, "Complaint reassigned successfully.")
            return redirect("admin_hacker_payout", complaint_id)

        # ------------------------------------------------
        # 3️⃣ MARK PAID
        # ------------------------------------------------
        if action == "mark_paid":

            payout = HackerPayout.objects.filter(
                complaint=complaint,
                status="PENDING"
            ).select_related("hacker__user").first()

            if not payout:
                messages.error(request, "No pending payout found.")
                return redirect("admin_hacker_payout", complaint_id)

            with transaction.atomic():

                payment = Payments.objects.create(
                    payer=request.user,
                    receiver=payout.hacker.user,
                    amount=payout.amount,
                    paid_for="HACKER_PAYOUT",
                    payment_method="MANUAL",
                    transaction_id=f"HP{complaint.id}{int(timezone.now().timestamp())}",
                    status="Paid"
                )

                payout.status = "PAID"
                payout.payment = payment
                payout.save()

            messages.success(request, "Hacker payout marked as PAID.")
            return redirect("admin_hacker_payout", complaint_id)

    # ==============================
    # FETCH DATA FOR DISPLAY
    # ==============================
    applications = Applications.objects.filter(
        complaint=complaint
    ).select_related("hacker__user")

    completion = getattr(complaint, "completion", None)

    payout = HackerPayout.objects.filter(
        complaint=complaint
    ).select_related("hacker__user", "payment").first()

    history = Complaint_Status_History.objects.filter(
        complaint=complaint
    ).order_by("-updated_at")

    return render(request, "admin-hacker-payout.html", {
        "complaint": complaint,
        "applications": applications,
        "completion": completion,
        "payout": payout,
        "history": history,
    })
