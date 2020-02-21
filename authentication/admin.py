from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'date_joined')
    # fields = ['username', 'first_name', 'last_name', 'email', 'password', 'is_staff', ]
    fieldsets = (
        (None, {
            'fields': ('username', 'first_name', 'last_name', 'email', 'password')
        }),
        ('User status', {
            'fields': ('is_staff',)
        }),
    )
