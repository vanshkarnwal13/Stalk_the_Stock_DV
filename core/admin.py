from django.contrib import admin
from .models import UserDetail, transaction

class UserDetailAdmin(admin.ModelAdmin):
    readonly_fields = ('payed_on','user')

admin.site.register(UserDetail,UserDetailAdmin)
admin.site.register(transaction)
