from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Asset, Booking, LocationHistory
from .forms import BookingForm


def home(request):
    """Render the main asset list page."""
    assets = Asset.objects.all()
    return render(request, 'assets/asset_list.html', {'assets': assets})


def asset_detail(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    bookings = asset.bookings.all()
    history = asset.history.all()
    return render(request, 'assets/asset_detail.html', {'asset': asset, 'bookings': bookings, 'history': history})


def book_asset(request, pk):
    """Display and handle the booking form for an asset.

    Saves contact fields and links the booking to request.user when available.
    """
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.asset = asset
            if request.user.is_authenticated:
                booking.user = request.user
            if booking.overlaps():
                messages.error(request, 'This booking overlaps an existing booking for the asset.')
            else:
                booking.save()
                messages.success(request, 'Booking created.')
                return redirect('asset_detail', pk=asset.pk)
    else:
        form = BookingForm(initial={'asset': asset})
    return render(request, 'assets/book_asset.html', {'form': form, 'asset': asset})


def asset_list(request):
    assets = Asset.objects.filter(available=True)
    return render(request, 'assets/assets_list.html', {'assets': assets})


from django.http import HttpResponse
from django.core.management import call_command
from django.contrib.auth import get_user_model

def init_db(request):
    """
    Runs migrations and sets up the initial database state.
    WARNING: Only for initial setup on serverless/paas where shell access is limited.
    """
    try:
        # Run standard migrations
        call_command('migrate')
        
        # Create a superuser if it doesn't exist
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            msg = "Migrations completed. Superuser 'admin' created (password: admin123)."
        else:
            msg = "Migrations completed. Superuser 'admin' already exists."
            
        # Seed Mikes Category and Subcategories
        from .models import Category, SubCategory
        mikes_cat, _ = Category.objects.get_or_create(name='Mikes')
        SubCategory.objects.get_or_create(category=mikes_cat, name='Wire mike')
        SubCategory.objects.get_or_create(category=mikes_cat, name='Wireless mike')
        
        msg += " Seeding for 'Mikes' category and subcategories successful."
        return HttpResponse(msg)
    except Exception as e:
        return HttpResponse(f"Error initializing DB: {str(e)}", status=500)
