from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from .forms import UserForm, UserProfileForm, LanguageProficiencyFormSet
from .models import UserProfile, Airport
from django.db.models import Q

@login_required
def profile_view(request):
    """
    View for displaying the user's profile.
    """
    user = request.user
    user_profile = user.profile

    return render(request, 'users/profile.html', {
        'user': user,
        'profile': user_profile,
    })

@login_required
@transaction.atomic
def profile_update(request):
    """
    View for updating the user's profile.
    """
    user = request.user
    user_profile = user.profile

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=user_profile)
        language_formset = LanguageProficiencyFormSet(request.POST, instance=user_profile)

        if user_form.is_valid() and profile_form.is_valid() and language_formset.is_valid():
            user_form.save()
            profile_form.save()
            language_formset.save()

            messages.success(request, 'Your profile was successfully updated!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=user_profile)
        language_formset = LanguageProficiencyFormSet(instance=user_profile)

    return render(request, 'users/profile_form.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'language_formset': language_formset,
    })

@login_required
def search_airports(request):
    """
    View for searching airports based on a query string.
    Returns JSON response with matching airports.
    """
    query = request.GET.get('q', '')
    if not query or len(query) < 2:
        return JsonResponse({'results': []})

    # Search for airports matching the query in name, city, or IATA code
    airports = Airport.objects.filter(
        Q(name__icontains=query) | 
        Q(city__icontains=query) | 
        Q(iata_code__icontains=query.upper())
    )[:20]  # Limit to 20 results for performance

    results = [
        {
            'id': airport.id,
            'text': f"{airport.name} ({airport.iata_code}) - {airport.city}, {airport.country.name}"
        }
        for airport in airports
    ]

    return JsonResponse({'results': results})
