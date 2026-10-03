from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import AdoptionRequest, Pet


class PetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = "__all__"
        read_only_fields = ["created_at"]


class AdoptionRequestSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = AdoptionRequest
        fields = ["id", "user", "pet", "phone", "address", "reason",
                  "previous_pet_experience", "message", "status", "created_at"]
        read_only_fields = ["status", "created_at"]  # status is changed by admin only

    def validate(self, attrs):
        if self.instance:
            attrs.pop("pet", None)  # pet cannot be changed after submitting
            if self.instance.status != AdoptionRequest.Status.PENDING:
                raise serializers.ValidationError("Only pending requests can be edited.")
            return attrs
        obj = AdoptionRequest(user=self.context["request"].user, **attrs)
        try:
            obj.clean()  # applies business rules 1 & 2
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return attrs
