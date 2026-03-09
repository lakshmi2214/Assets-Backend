from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Location(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Sub-Categories"
        unique_together = ('category', 'name')

    def __str__(self):
        return f"{self.category.name} > {self.name}"

class Asset(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets')
    description = models.TextField(blank=True)
    serial_number = models.CharField(max_length=200, blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    available = models.BooleanField(default=True)
    total_quantity = models.PositiveIntegerField(default=1)
    # Image and detailed specs
    image = models.ImageField(upload_to='assets/images/', null=True, blank=True)
    details = models.TextField(blank=True, help_text='Detailed specs (e.g. camera, battery, lens, etc)')

    def __str__(self):
        return f"{self.name} ({self.serial_number})" if self.serial_number else self.name

class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'
        CANCELLATION_REQUESTED = 'cancellation_requested', 'Cancellation Requested'
        CANCELLED = 'cancelled', 'Cancelled'
        RECEIVED = 'received', 'Received'
        RETURNED = 'returned', 'Returned'

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.PENDING)
    quantity = models.PositiveIntegerField(default=1)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    
    # Handover images
    received_image = models.ImageField(upload_to='bookings/received/', null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)
    returned_image = models.ImageField(upload_to='bookings/returned/', null=True, blank=True)
    returned_at = models.DateTimeField(null=True, blank=True)

    purpose = models.CharField(max_length=255, blank=True)
    # Contact details (for guest bookings or extra info)
    contact_name = models.CharField(max_length=200, blank=True)

    contact_email = models.EmailField(blank=True)
    contact_address = models.TextField(blank=True)
    contact_mobile = models.CharField(max_length=30, blank=True)
    contact_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings_contact')
    cancellation_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_datetime']
        permissions = [
            ('can_accept_booking', 'Can accept booking'),
            ('can_reject_booking', 'Can reject booking'),
            ('can_cancel_booking', 'Can cancel booking'),
        ]

    def __str__(self):
        return f"{self.asset.name} booked by {self.user} ({self.start_datetime} - {self.end_datetime})"

    def overlaps(self):
        from datetime import timedelta
        from django.db.models import Sum
        
        # Consider bookings that are Pending, Accepted, or Received (in use) as blocking quantity
        blocking_statuses = [
            Booking.Status.PENDING,
            Booking.Status.ACCEPTED,
            Booking.Status.RECEIVED
        ]
        
        # Buffer to ensure gap between bookings
        buffer = timedelta(hours=1)
        check_start = self.start_datetime - buffer
        check_end = self.end_datetime + buffer

        # Find all overlapping bookings
        qs = Booking.objects.filter(
            asset=self.asset, 
            status__in=blocking_statuses
        ).exclude(pk=self.pk)
        
        overlapping_bookings = qs.filter(
            start_datetime__lt=check_end,
            end_datetime__gt=check_start
        )

        # For simple multi-quantity, we check if the sum of quantity at ANY point in our range exceeds limit.
        # This is a bit complex for a simple Django method without specific interval tree, 
        # so we'll check peak capacity within the overlapping set.
        
        # Simplified: Sum up the quantity of all concurrently overlapping bookings.
        # To be more precise, we should check every start/end time in the range.
        test_points = [check_start, check_end]
        for b in overlapping_bookings:
            test_points.append(b.start_datetime)
            test_points.append(b.end_datetime)
            
        test_points = [p for p in test_points if check_start <= p <= check_end]
        
        for t in test_points:
            booked_at_t = qs.filter(
                start_datetime__lte=t,
                end_datetime__gte=t
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            if booked_at_t + self.quantity > self.asset.total_quantity:
                return True
        return False

class CancellationRequest(Booking):
    class Meta:
        proxy = True
        verbose_name = 'Cancellation Request'
        verbose_name_plural = 'Cancellation Requests'

class LocationHistory(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='history')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.asset.name} @ {self.location} on {self.timestamp}"

