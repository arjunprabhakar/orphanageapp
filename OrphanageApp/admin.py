from django.contrib import admin

from OrphanageApp.models import *
from django.contrib.auth.models import Group,User


# Register your models here.
admin.site.register(tbl_orphanage)
# admin.site.register(tbl_leave)
# admin.site.register(donations)
# admin.site.register(AssignedVolunteer)
# admin.site.register(tbl_category)
# admin.site.register(tbl_donor)
# admin.site.register(tbl_login)
# admin.site.register(tbl_donor_new_address)
# admin.site.register(tbl_amount_donations)

# class MarkAdmin(admin.ModelAdmin):
#     list_display=['student','mark1']
# admin.site.register(marks,MarkAdmin)

admin.site.unregister(Group)
admin.site.unregister(User)

