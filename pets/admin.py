from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from .models import AdoptionRequest, Pet


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ("name", "animal_type", "breed", "age", "gender", "location", "status", "created_at")
    list_filter = ("animal_type", "gender", "status")
    list_editable = ("status",)
    search_fields = ("name", "breed", "location")


@admin.register(AdoptionRequest)
class AdoptionRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "pet", "created_at", "phone", "short_reason", "status")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "pet__name", "phone")
    actions = ["approve_requests", "reject_requests"]

    @admin.display(description="Reason")
    def short_reason(self, obj):
        return obj.reason[:50] + ("..." if len(obj.reason) > 50 else "")

    def get_readonly_fields(self, request, obj=None):
        # When editing, admin can only change the status
        if obj:
            return ("user", "pet", "phone", "address", "reason",
                    "previous_pet_experience", "message", "created_at")
        return ()

    def _set_status(self, request, queryset, status):
        done = 0
        for obj in queryset.filter(status=AdoptionRequest.Status.PENDING):
            obj.status = status
            try:
                obj.full_clean()
                obj.save()
                done += 1
            except ValidationError as e:
                self.message_user(request, f"{obj}: {'; '.join(e.messages)}", messages.ERROR)
        self.message_user(request, f"{done} request(s) marked {status}.")

    @admin.action(description="Approve selected pending requests")
    def approve_requests(self, request, queryset):
        self._set_status(request, queryset, AdoptionRequest.Status.APPROVED)

    @admin.action(description="Reject selected pending requests")
    def reject_requests(self, request, queryset):
        self._set_status(request, queryset, AdoptionRequest.Status.REJECTED)
