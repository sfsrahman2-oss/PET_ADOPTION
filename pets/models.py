from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Q
from django.urls import reverse


class Pet(models.Model):
    class AnimalType(models.TextChoices):
        DOG = "Dog", "Dog"
        CAT = "Cat", "Cat"
        BIRD = "Bird", "Bird"
        RABBIT = "Rabbit", "Rabbit"
        OTHER = "Other", "Other"

    class Gender(models.TextChoices):
        MALE = "Male", "Male"
        FEMALE = "Female", "Female"

    class Status(models.TextChoices):
        AVAILABLE = "Available", "Available"
        ADOPTED = "Adopted", "Adopted"

    name = models.CharField(max_length=100)
    animal_type = models.CharField(max_length=20, choices=AnimalType.choices, default=AnimalType.DOG)
    breed = models.CharField(max_length=100, blank=True)
    age = models.PositiveSmallIntegerField(help_text="Age in years")
    gender = models.CharField(max_length=10, choices=Gender.choices)
    location = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="pets/", blank=True, null=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.AVAILABLE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.animal_type})"

    @property
    def is_available(self):
        return self.status == self.Status.AVAILABLE

    def get_absolute_url(self):
        return reverse("pet_detail", args=[self.pk])


class AdoptionRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        APPROVED = "Approved", "Approved"
        REJECTED = "Rejected", "Rejected"

    ACTIVE_STATUSES = (Status.PENDING, Status.APPROVED)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="adoption_requests")
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name="adoption_requests")
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    reason = models.TextField(verbose_name="Why do you want this pet?")
    previous_pet_experience = models.BooleanField(default=False, verbose_name="Have you owned a pet before?")
    message = models.TextField(blank=True, verbose_name="Additional message")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            # DB-level guard for Rule 2: one active request per user per pet
            models.UniqueConstraint(
                fields=["user", "pet"],
                condition=Q(status__in=["Pending", "Approved"]),
                name="unique_active_request_per_user_pet",
            )
        ]

    def __str__(self):
        return f"{self.user} -> {self.pet.name} [{self.status}]"

    def clean(self):
        if not self.pet_id:
            return
        if self._state.adding:
            # Rule 1: only available pets can be adopted
            if not self.pet.is_available:
                raise ValidationError("This pet has already been adopted.")
            # Rule 2: no duplicate active requests
            if self.user_id and AdoptionRequest.objects.filter(
                user_id=self.user_id, pet_id=self.pet_id, status__in=self.ACTIVE_STATUSES
            ).exists():
                raise ValidationError("You already have an active request for this pet.")
        # Rule 3: a pet can only be approved once
        if self.status == self.Status.APPROVED and AdoptionRequest.objects.filter(
            pet_id=self.pet_id, status=self.Status.APPROVED
        ).exclude(pk=self.pk).exists():
            raise ValidationError("Another request for this pet is already approved.")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)
            if self.status == self.Status.APPROVED:
                Pet.objects.filter(pk=self.pet_id).update(status=Pet.Status.ADOPTED)
                # close other pending requests for the same pet
                AdoptionRequest.objects.filter(
                    pet_id=self.pet_id, status=self.Status.PENDING
                ).exclude(pk=self.pk).update(status=self.Status.REJECTED)
