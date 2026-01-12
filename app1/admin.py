from django.contrib import admin
from django.contrib import admin
from .models import (
    User, Role, Admin_Profile,
    Blogs, Blog_Comments, Blog_Stats,
    Awareness_Sessions, Session_Feedback,
    Business_Profile, Hacker_Profile,
    Payments, Invoices, Banking_Info,
    Complaints, Complaint_Status_History,
    Audit_Log
)

admin.site.register(User)
admin.site.register(Role)
admin.site.register(Admin_Profile)

admin.site.register(Blogs)
admin.site.register(Blog_Comments)
admin.site.register(Blog_Stats)

admin.site.register(Awareness_Sessions)
admin.site.register(Session_Feedback)

admin.site.register(Business_Profile)
admin.site.register(Hacker_Profile)

admin.site.register(Payments)
admin.site.register(Invoices)
admin.site.register(Banking_Info)

admin.site.register(Complaints)
admin.site.register(Complaint_Status_History)

admin.site.register(Audit_Log)
