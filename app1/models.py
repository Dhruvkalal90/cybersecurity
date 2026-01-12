from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, Group, Permission


# =========================
# 1. USERS & ROLES
# =========================

class Role(models.Model):
    ROLE_CHOICES = [
        ('BUSINESS', 'Business'),
        ('HACKER', 'Hacker'),
        ('ADMIN', 'Admin'),
    ]
    name = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.name

from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username=None, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not username:
            raise ValueError("Username is required")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, username=email, password=password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(unique=True,max_length=50)
    email = models.EmailField(unique=True)
    role = models.ForeignKey('Role', on_delete=models.CASCADE, null=True, blank=True)
    date_created = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()  # ✅ Use our new manager here

    # prevent reverse accessor clashes
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_groups",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",
        blank=True
    )

    def __str__(self):
        return self.email




# =========================
# 2. BUSINESS PROFILE       - gst 
# =========================

class Business_Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=150)
    industry = models.CharField(max_length=100, blank=True)
    contact_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    gstin = models.CharField(max_length=20, blank=True)   # ADDED
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name



# =========================
# 3. HACKER PROFILE             
# =========================

class Hacker_Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150, blank=True)         # ADDED
    specialization = models.CharField(max_length=150, blank=True)    # ADDED
    photo = models.ImageField(upload_to="hacker_photos/", blank=True, null=True)  # ADDED
    contact_number = models.CharField(max_length=20, blank=True)
    certificate_number = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.email



# =========================
# 4. ADMIN PROFILE
# =========================

class Admin_Profile(models.Model):
    POSITION_CHOICES = [
        ("SYSTEM_ADMIN", "System Admin"),
        ("STAFF", "Staff"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    position = models.CharField(
        max_length=100,
        choices=POSITION_CHOICES,
        default="SYSTEM_ADMIN"
    )

    def __str__(self):
        return f"{self.user.email} ({self.get_position_display()})"



# =========================
# 5. COMPLAINTS
# =========================

class Complaints(models.Model):
    business = models.ForeignKey(Business_Profile, on_delete=models.CASCADE)

    # from form
    title = models.CharField(max_length=200,blank=True, null=True)
    category = models.CharField(max_length=50,blank=True, null=True)  
    description = models.TextField(blank=True, null=True)

    # new fields from your HTML form
    service_type = models.CharField(max_length=20, choices=[
        ("REPORT", "Report Only"),
        ("GUIDE", "Report + Guide"),
        ("COMPLETE", "Complete Solution"),
    ],blank=True, null=True)

    date_of_occurrence = models.DateField(blank=True, null=True)
    additional_notes = models.TextField(blank=True, null=True)

    # system fields
    date_submitted = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50, default="Pending",blank=True, null=True)
    assigned_hacker = models.ForeignKey('Hacker_Profile', on_delete=models.SET_NULL, null=True, blank=True)
    priority = models.CharField(max_length=20, default="Medium")

    def __str__(self):
        return f"{self.title} - {self.business.company_name}"

class ComplaintFiles(models.Model):
    complaint = models.ForeignKey(Complaints, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to="complaint_files/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File for {self.complaint.title}"



# =========================
# 6. COMPLAINT STATUS HISTORY
# =========================

class Complaint_Status_History(models.Model):
    complaint = models.ForeignKey(Complaints, on_delete=models.CASCADE)
    old_status = models.CharField(max_length=50)
    new_status = models.CharField(max_length=50)
    updated_at = models.DateTimeField(default=timezone.now)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.complaint.title} - {self.new_status}"


# =========================
# 7. APPLICATIONS
# =========================

class Applications(models.Model):
    hacker = models.ForeignKey(Hacker_Profile, on_delete=models.CASCADE)
    complaint = models.ForeignKey(Complaints, on_delete=models.CASCADE)
    applied_on = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50, default="Pending")

    def __str__(self):
        return f"{self.hacker.user.email} applied for {self.complaint.title}"


# =========================
# 8. PAYMENTS
# =========================

class Payments(models.Model):
    payer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payer',blank=True,null=True)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver',blank=True,null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=50, default="Pending")
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.transaction_id} - {self.status}"


# =========================
# 9. INVOICES
# =========================

class Invoices(models.Model):
    payment = models.OneToOneField(Payments, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50, unique=True)
    date_issued = models.DateTimeField(default=timezone.now)
    pdf_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.invoice_number


# =========================
# 10. BANKING INFO
# =========================

class Banking_Info(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_holder_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    ifsc_code = models.CharField(max_length=20)
    bank_name = models.CharField(max_length=100)
    branch_name = models.CharField(max_length=100, blank=True)
    upi_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.bank_name}"


# =========================
# 11. AWARENESS SESSIONS
# =========================

class Awareness_Sessions(models.Model):

    SESSION_MODE = [
        ("ONLINE", "Online"),
        ("OFFLINE", "Offline"),
    ]

    PACKAGE_CHOICES = [
        ("BASIC_ONLINE", "Basic Online"),
        ("STANDARD_ONLINE", "Standard Online"),
        ("PREMIUM_ONLINE", "Premium Online"),
        ("BASIC_OFFLINE", "Basic Offline"),
        ("STANDARD_OFFLINE", "Standard Offline"),
        ("PREMIUM_OFFLINE", "Premium Offline"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    PAYMENT_STATUS = [
        ("UNPAID", "Unpaid"),
        ("PROCESSING", "Processing"),
        ("PAID", "Paid"),
        ("FAILED", "Failed"),
        ("REFUNDED", "Refunded"),
    ]

    # ---- BUSINESS (PRE-FILLED) ----
    business = models.ForeignKey(Business_Profile, on_delete=models.CASCADE, null=True, blank=True)

    # ---- ORGANIZATION DETAILS ----
    company_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    # ---- SESSION DETAILS ----
    session_mode = models.CharField(max_length=10, choices=SESSION_MODE)
    package = models.CharField(max_length=50, choices=PACKAGE_CHOICES)
    preferred_date = models.DateField()
    location = models.TextField(blank=True, null=True)

    # ---- PRICING ----
    participants = models.PositiveIntegerField(default=50)
    package_price = models.PositiveIntegerField(default=0)
    extra_price = models.PositiveIntegerField(default=0)
    total_price = models.PositiveIntegerField(default=0)

    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="UNPAID")

    # ---- SYSTEM ----
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.company_name} | {self.session_mode} | {self.payment_status}"


# =========================
# 12. SESSION FEEDBACK
# =========================

class Session_Feedback(models.Model):
    session = models.ForeignKey(Awareness_Sessions, on_delete=models.CASCADE)
    business = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.PositiveIntegerField(default=5)
    feedback_text = models.TextField(blank=True)
    submitted_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.business.email if self.business else 'Unknown'} - Session {self.session.id}"



# =========================
# 13. BLOGS
# =========================

class Blogs(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    content = models.TextField()

    # Featured Image
    featured_image = models.ImageField(
        upload_to="blog_images/",
        null=True,
        blank=True,
        default="blog_images/default_blog.png"
    )

    category = models.CharField(max_length=100, blank=True)

    # Blog timestamps
    created_on = models.DateTimeField(default=timezone.now)
    updated_on = models.DateTimeField(auto_now=True)

    # Views only (as requested)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


# =========================
# 14. BLOG COMMENTS  (Not used but kept for future)
# =========================

class Blog_Comments(models.Model):
    blog = models.ForeignKey(Blogs, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.email} on {self.blog.title}"


# =========================
# 15. BLOG STATS (Optional)
# =========================
# Since you said “we only need views”, this model is NOT required.
# Keeping it here if you need analytics later.

class Blog_Stats(models.Model):
    blog = models.OneToOneField(Blogs, on_delete=models.CASCADE)
    total_likes = models.PositiveIntegerField(default=0)
    total_comments = models.PositiveIntegerField(default=0)
    total_views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Stats for {self.blog.title}"


# =========================
# 16. AUDIT LOG
# =========================

class Audit_Log(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=200)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    details = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user} - {self.action}"


# =========================
# 17. NOTIFICATIONS
# =========================

class Notifications(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    link = models.URLField(blank=True)
    created_on = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"To: {self.recipient.email}"
