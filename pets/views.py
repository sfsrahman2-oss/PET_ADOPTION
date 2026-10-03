from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AdoptionForm, RegisterForm
from .models import AdoptionRequest, Pet


def home(request):
    latest = Pet.objects.filter(status=Pet.Status.AVAILABLE)[:3]
    return render(request, "home.html", {"latest": latest})


def pet_list(request):
    g = request.GET
    pets = Pet.objects.all()
    if g.get("name"):
        pets = pets.filter(name__icontains=g["name"])
    if g.get("animal_type"):
        pets = pets.filter(animal_type=g["animal_type"])
    if g.get("breed"):
        pets = pets.filter(breed__icontains=g["breed"])
    if g.get("gender"):
        pets = pets.filter(gender=g["gender"])
    if g.get("location"):
        pets = pets.filter(location__icontains=g["location"])
    if g.get("status"):
        pets = pets.filter(status=g["status"])

    page_obj = Paginator(pets, 6).get_page(g.get("page"))
    params = g.copy()
    params.pop("page", None)
    return render(request, "pet_list.html", {
        "page_obj": page_obj,
        "querystring": params.urlencode(),
        "f": g,
        "animal_types": Pet.AnimalType.choices,
        "genders": Pet.Gender.choices,
        "statuses": Pet.Status.choices,
    })


def pet_detail(request, pk):
    pet = get_object_or_404(Pet, pk=pk)
    has_active = request.user.is_authenticated and AdoptionRequest.objects.filter(
        user=request.user, pet=pet, status__in=AdoptionRequest.ACTIVE_STATUSES
    ).exists()
    return render(request, "pet_detail.html", {"pet": pet, "has_active": has_active})


@login_required
def adopt(request, pk):
    pet = get_object_or_404(Pet, pk=pk)
    if not pet.is_available:
        messages.error(request, "This pet has already been adopted.")
        return redirect(pet)
    if AdoptionRequest.objects.filter(
        user=request.user, pet=pet, status__in=AdoptionRequest.ACTIVE_STATUSES
    ).exists():
        messages.warning(request, "You already have an active request for this pet.")
        return redirect("my_requests")

    instance = AdoptionRequest(user=request.user, pet=pet)
    form = AdoptionForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Your application for {pet.name} was submitted.")
        return redirect("my_requests")
    return render(request, "adopt.html", {"form": form, "pet": pet})


@login_required
def my_requests(request):
    reqs = AdoptionRequest.objects.filter(user=request.user).select_related("pet")
    return render(request, "my_requests.html", {"requests": reqs})


@login_required
def profile(request):
    reqs = AdoptionRequest.objects.filter(user=request.user)
    stats = {s: reqs.filter(status=s).count() for s in AdoptionRequest.Status.values}
    return render(request, "profile.html", {"stats": stats, "total": reqs.count()})


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Welcome! Your account has been created.")
        return redirect("home")
    return render(request, "registration/register.html", {"form": form})
