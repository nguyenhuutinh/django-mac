from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from common.models import TokenInfo
# the module name is app_name.models
from common.models import DownloadInfo
# Register your models to admin site, then you can add, edit, delete and search your models in Django admin site.
from .models import User


class CustomUserAdmin(UserAdmin):
    list_display = ("id", "email", "created", "modified")
    list_filter = ("is_active", "is_staff", "groups")
    search_fields = ("email",)
    ordering = ("email",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Permissions"),
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),)


admin.site.register(User, CustomUserAdmin)
admin.site.register(DownloadInfo)
admin.site.register(TokenInfo)
