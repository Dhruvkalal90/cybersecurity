from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .decorators import role_required
from .models import User, Business_Profile, Hacker_Profile, Role, Awareness_Sessions,Blogs,Complaints,ComplaintFiles,Applications,Payments
from django.utils import timezone
from django.db.models import F,Q
from django.db import transaction
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


# ===============================
# HOME & STATIC PAGES
# ===============================
def index(request):
    if request.user.is_authenticated:
        return redirect("dashboard")  # use URL name
    return render(request, "index.html")

def pnp(request):
    return render(request, "pnp.html")


# ===============================
# AJAX: CHECK USERNAME
# ===============================

def check_username(request):
    username = request.GET.get('username', '').strip()
    exists = User.objects.filter(username__iexact=username).exists()
    return JsonResponse({'exists': exists})



# ===============================
# SIGNUP VIEW
# ===============================

from django.contrib.auth import authenticate, login

def signup_view(request):
    if request.method == 'POST':
        username=request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role_type = request.POST.get('role')

        # Basic validation
        if not email or not password or not role_type:
            messages.error(request, "All fields are required.")
            return redirect('signup')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('signup')

        try:
            # Get role
            role, _ = Role.objects.get_or_create(name=role_type.upper())

            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=role
            )

            # AUTO LOGIN USER ✔
            authenticated_user = authenticate(request, username=email, password=password)
            if authenticated_user:
                login(request, authenticated_user)

            # Create profile and redirect
            if role_type.lower() == 'business':
                Business_Profile.objects.create(user=user)
                return redirect('business-profile-form')

            elif role_type.lower() == 'hacker':
                Hacker_Profile.objects.create(user=user)
                return redirect('hacker-profile-form')

            else:
                return redirect('login')

        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect('signup')

    return render(request, 'signup.html')


# ===============================
# LOGIN VIEW
# ===============================

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not email or not password:
            messages.error(request, "Please fill in all fields.")
            return redirect('login')

        # IMPORTANT: Django expects "username", not "email"
        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            messages.success(request, f"Welcome back, { user.username}!")

            # Role-based redirect
            role = user.role.name.lower() if user.role else None

            if role:
                return redirect("dashboard")
            else:
                messages.warning(request, "No role assigned.")
                return redirect('login')

        else:
            messages.error(request, "Invalid email or password.")
            return redirect('login')

    return render(request, 'login.html')


# ===============================
# LOGOUT
# ===============================

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')


# ===============================
# PROFILE COMPLETION FORMS
# ===============================

@login_required
def business_profile_form(request):
    return render(request, "business-detail-form.html")

@login_required
def hacker_profile_form(request):
    return render(request, "hacker-details-form.html")


# ===============================
# DASHBOARDS (Protected)
# ===============================
@login_required
def dashboard(request):
    user = request.user

    # Admin redirect logic
    if user.role_id == 3:
        return redirect("admin_dashboard")

    # If hacker, show new opportunities
    if user.role.name.lower() == "hacker":
        hacker = Hacker_Profile.objects.get(user=user)

        # Complaints hacker did NOT apply to yet
        applied_ids = Applications.objects.filter(hacker=hacker).values_list("complaint_id", flat=True)

        latest_complaints = Complaints.objects.exclude(
            id__in=applied_ids
        ).order_by("-date_submitted")[:3]

        return render(request, "dashboard.html", {
            "opportunities": latest_complaints
        })
    elif user.role.name.lower() == "business":
        business = Business_Profile.objects.get(user=user)

    # Get all complaints of this business
        all_complaints = Complaints.objects.filter(business=business)

        # Stats
        total = all_complaints.count()
        pending = all_complaints.filter(status="Pending").count()
        in_progress = all_complaints.filter(status="In Progress").count()
        resolved = all_complaints.filter(status="Resolved").count()

        # Recent 5 complaints
        recent = all_complaints.order_by("-date_submitted")[:5]

        return render(request, "dashboard.html", {
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "resolved": resolved,
            "recent_complaints": recent,
        })
    # Default dashboard for others
    return render(request, "dashboard.html")


"""
@role_required("hacker")
def hacker_dashboard(request):
    return render(request, "hacker-dashboard.html")

@role_required("business")
def business_dashboard(request):
    return render(request, "business-dashboard.html")
    
"""
@login_required
def hacker_profile_form(request):
    user = request.user

    # Fetch or create hacker profile
    hacker_profile, created = Hacker_Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        contact_number = request.POST.get('contact_number')
        specialization = request.POST.get('specialization')
        certificate_number = request.POST.get('certificate_number')
        photo = request.FILES.get('photo')

        # Basic Validation
        if not (full_name and contact_number and specialization and certificate_number and photo):
            messages.error(request, "All fields are required.")
            return redirect('hacker-profile-form')

        # Save data
        hacker_profile.full_name = full_name
        hacker_profile.contact_number = contact_number
        hacker_profile.specialization = specialization
        hacker_profile.certificate_number = certificate_number

        if photo:
            hacker_profile.photo = photo

        hacker_profile.save()

        messages.success(request, "Your CEH profile details have been submitted!")
        return redirect('dashboard')

    return render(request, "hacker-details-form.html")

@login_required
def business_profile_form(request):
    user = request.user

    # User must be business role
    if user.role.name.lower() != "business":
        messages.error(request, "Unauthorized access.")
        return redirect("index")

    profile = Business_Profile.objects.get(user=user)

    if request.method == "POST":
        company_name = request.POST.get("company_name")
        contact = request.POST.get("contact_number")
        address = request.POST.get("address")
        gstin = request.POST.get("gstin")

        # Validation
        if not company_name or not contact or not address or not gstin:
            messages.error(request, "All fields are required.")
            return redirect("business-profile-form")

        # Save data
        profile.company_name = company_name
        profile.contact_number = contact
        profile.address = address
        profile.gstin = gstin
        profile.save()

        messages.success(request, "Business profile saved successfully!")
        return redirect("business_dashboard")

    return render(request, "business-detail-form.html")

@role_required("business", "dashboard")
@login_required
def book_session(request):

    business = get_object_or_404(Business_Profile, user=request.user)
    pending = request.session.get("pending_awareness_booking")
    if request.method == "POST":

        # ---- Collect data ----
        data = {
            "company_name": request.POST.get("companyName"),
            "contact_person": request.POST.get("contactPerson"),
            "phone": request.POST.get("phone"),
            "email": request.POST.get("email"),
            "session_mode": request.POST.get("sessionMode"),
            "package": request.POST.get("package"),
            "preferred_date": request.POST.get("preferredDate"),
            "location": request.POST.get("location"),
            "participants": int(request.POST.get("participants", 50)),
            "package_price": int(request.POST.get("package_price", 0)),
            "extra_price": int(request.POST.get("extra_price", 0)),
            "total_price": int(request.POST.get("total_price", 0)),
        }

        required = [
            data["company_name"], data["contact_person"], data["phone"],
            data["email"], data["session_mode"], data["package"], data["preferred_date"]
        ]

        if any(not x for x in required):
            messages.error(request, "Please complete all required fields.")
            return redirect("book_session")

        if data["session_mode"].lower() == "offline" and not data["location"]:
            messages.error(request, "Location is required for offline sessions.")
            return redirect("book_session")

        # ---- Store TEMP booking in session ----
        request.session["pending_awareness_booking"] = data
        # ---- Clear old Razorpay order ----
        request.session.pop("razorpay_order_id", None)
        # ---- Create Razorpay order ----
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        order = client.order.create({
            "amount": data["total_price"] * 100,
            "currency": "INR",
            "payment_capture": 1
        })

        request.session["razorpay_order_id"] = order["id"]

        return redirect("pay_session")

    return render(request, "book-session.html", {"business": business,"pending": pending})


@login_required
def pay_awareness_session(request):

    booking = request.session.get("pending_awareness_booking")
    order_id = request.session.get("razorpay_order_id")

    if not booking or not order_id:
        messages.error(request, "No pending payment found.")
        return redirect("book_session")

    context = {
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "order_id": order_id,
        "amount": booking["total_price"] * 100,
        "company": booking["company_name"],
        "email": booking["email"],
        "phone": booking["phone"],
    }
    print(context)
    return render(request, "razorpay_checkout.html", context)


@csrf_exempt
def payment_success(request):
    if request.method != "POST":
        return redirect("dashboard")

    payment_id = request.POST.get("razorpay_payment_id")
    order_id = request.POST.get("razorpay_order_id")

    booking = request.session.get("pending_awareness_booking")
    saved_order = request.session.get("razorpay_order_id")
    print(payment_id,order_id,booking,saved_order)
    if not booking or order_id != saved_order:
        messages.error(request, "Invalid or expired payment.")
        return redirect("dashboard")

    business = Business_Profile.objects.get(user=request.user)

    # ---- CREATE SESSION (ONLY NOW) ----
    session = Awareness_Sessions.objects.create(
        business=business,
        company_name=booking["company_name"],
        contact_person=booking["contact_person"],
        phone=booking["phone"],
        email=booking["email"],
        session_mode=booking["session_mode"].upper(),
        package=booking["package"].upper(),
        preferred_date=booking["preferred_date"],
        location=booking["location"] or "Online",
        participants=booking["participants"],
        package_price=booking["package_price"],
        extra_price=booking["extra_price"],
        total_price=booking["total_price"],
        payment_status="PAID",
        status="APPROVED",
    )

    Payments.objects.create(
        payer=business.user,
        amount=session.total_price,
        payment_method="RAZORPAY",
        transaction_id=payment_id,
        status="Paid"
    )

    # ---- CLEAN SESSION ----
    del request.session["pending_awareness_booking"]
    del request.session["razorpay_order_id"]

    messages.success(request, "Payment successful! Session booked.")
    return redirect("dashboard")




@role_required("hacker","dashboard")
@login_required
def blog_mgmt_view(request):
    # ---- POST: Create Blog ----
    if request.method == "POST":
        title = request.POST.get("title")
        category = request.POST.get("category")
        content = request.POST.get("content")
        image = request.FILES.get("featured_image")

        if not title or not content:
            messages.error(request, "Title and content are required.")
            return redirect("hacker_blog_management")

        blog = Blogs.objects.create(
            author=request.user,
            title=title,
            category=category,
            content=content,
            featured_image=image if image else "blog_images/default_blog.png",
        )

        messages.success(request, "Blog published successfully!")
        return redirect("blog_mgmt")

    # ---- GET: Show user's blogs ----
    user_blogs = Blogs.objects.filter(author=request.user).order_by("-created_on")

    return render(request, "hacker-blog-management.html", {
        "blogs": user_blogs,
    })



def blog_list(request):
    search = request.GET.get("search", "")
    category = request.GET.get("category", "")
    sort = request.GET.get("sort", "latest")

    blogs = Blogs.objects.all()

    # SEARCH
    if search:
        blogs = blogs.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search)
        )

    # CATEGORY
    if category and category != "all":
        blogs = blogs.filter(category__iexact=category)

    # SORTING
    if sort == "latest":
        blogs = blogs.order_by("-created_on")
    elif sort == "popular":
        blogs = blogs.order_by("-views")

    return render(request, "blog-list.html", {
        "blogs": blogs,
        "search": search,
        "selected_category": category,
        "selected_sort": sort
    })


def read_blog(request, blog_id):
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

@role_required("hacker","dashboard")
@login_required
def edit_blog(request, blog_id):
    blog = get_object_or_404(Blogs, id=blog_id, author=request.user)

    if request.method == "POST":
        blog.title = request.POST["title"]
        blog.category = request.POST["category"]
        blog.content = request.POST["content"]

        if request.FILES.get("featured_image"):
            blog.featured_image = request.FILES["featured_image"]

        blog.save()
        return redirect("blog_mgmt")

@role_required("hacker","dashboard")
@login_required
def delete_blog(request, blog_id):
    blog = get_object_or_404(Blogs, id=blog_id, author=request.user)

    if request.method == "POST":
        blog.delete()
        messages.success(request, "Blog deleted successfully!")
        return redirect("blog_mgmt")

    return render(request, "confirm-delete.html", {"blog": blog})

@role_required("business","dashboard")
@login_required
def awareness_session_list(request):
    business_profile = get_object_or_404(Business_Profile, user=request.user)

    sessions = Awareness_Sessions.objects.filter(business=business_profile).order_by("id")

    # Ensure minimum 5 rows
    total = len(sessions)
    empty_rows = range(5 - total) if total < 5 else []

    return render(request, "business-awarness-list.html", {
        "sessions": sessions,
        "empty_rows": empty_rows,
    })

@role_required("business","dashboard")
def submit_complaint(request):
    if request.method == "POST":
        title = request.POST.get("title")
        category = request.POST.get("category")
        description = request.POST.get("description")
        service_type = request.POST.get("serviceType")
        date_of_occurrence = request.POST.get("date_of_occurrence")
        notes = request.POST.get("additional_notes")
        files = request.FILES.getlist("files")

        business = Business_Profile.objects.get(user=request.user)

        complaint = Complaints.objects.create(
            business=business,
            title=title,
            category=category,
            description=description,
            service_type=service_type.upper(),
            date_of_occurrence=date_of_occurrence,
            additional_notes=notes,
        )

        # save multiple files
        for f in files:
            ComplaintFiles.objects.create(
                complaint=complaint,
                file=f
            )

        messages.success(request, "Complaint submitted successfully!")
        return redirect("dashboard")

    return render(request, "submit-complaint.html")

@role_required("business","dashboard")
@login_required
def business_complaint_list(request):
    business_profile = get_object_or_404(Business_Profile, user=request.user)

    complaints = Complaints.objects.filter(business=business_profile).order_by("id")

    # Ensure minimum 5 rows
    total = len(complaints)
    empty_rows = range(5 - total) if total < 5 else []

    return render(request, "business-complaints-list.html", {
        "complaints": complaints,
        "empty_rows": empty_rows,
    })

@role_required("hacker","dashboard")
@login_required
def hacker_apply_complaint(request):
    user = request.user

    # hacker profile
    try:
        hacker = Hacker_Profile.objects.get(user=user)
    except Hacker_Profile.DoesNotExist:
        messages.error(request, "You must complete your hacker profile first.")
        return redirect("hacker-profile-form")

    # Complaints hacker already applied for
    applied_ids = Applications.objects.filter(hacker=hacker).values_list("complaint_id", flat=True)

    # Complaints available to hacker
    complaints = Complaints.objects.exclude(id__in=applied_ids).order_by("date_submitted")

    return render(request, "hacker-apply-complaint.html", {
        "complaints": complaints,
    })

@role_required("hacker", "dashboard")
@login_required
def apply_to_complaint(request, complaint_id):
    hacker = get_object_or_404(Hacker_Profile, user=request.user)
    complaint = get_object_or_404(Complaints, id=complaint_id)

    # Block if already assigned
    if complaint.assigned_hacker is not None:
        messages.error(request, "This complaint has already been assigned.")
        return redirect("hacker_apply_complaint")

    # Block duplicate application
    if Applications.objects.filter(hacker=hacker, complaint=complaint).exists():
        messages.warning(request, "You have already applied for this complaint.")
        return redirect("hacker_apply_complaint")

    if request.method == "POST":
        try:
            with transaction.atomic():
                # Re-check inside transaction (important for FCFS)
                complaint = Complaints.objects.select_for_update().get(id=complaint_id)

                if complaint.assigned_hacker is not None:
                    messages.error(request, "This complaint was just assigned to another hacker.")
                    return redirect("hacker_apply_complaint")

                # Create application
                Applications.objects.create(
                    hacker=hacker,
                    complaint=complaint,
                    status="Accepted"
                )

                # Assign hacker to complaint
                complaint.assigned_hacker = hacker
                complaint.status = "In Progress"
                complaint.save()

                messages.success(request, "🎉 You have been assigned this complaint!")
                return redirect("dashboard")

        except Exception as e:
            messages.error(request, "Something went wrong. Please try again.")
            return redirect("hacker_apply_complaint")

    return redirect("hacker_apply_complaint")

@login_required
def profile(request):
    user=request.user
    if request.user.role_id == 1:
        Profile=Hacker_Profile.objects.get(user=user)
    elif request.user.role_id == 2:
        Profile=Business_Profile.objects.get(user=user)
    else:
        return redirect("dashboard")
    return render(request,"profile.html",{"profile":Profile})