from django.contrib import admin
from .models import Asset, Booking, Location, LocationHistory, CancellationRequest, Category, SubCategory

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'subcategory', 'serial_number', 'location', 'available', 'thumbnail')
    list_filter = ('available', 'category', 'subcategory', 'location')
    search_fields = ('name', 'serial_number')
    readonly_fields = ()

    def thumbnail(self, obj):
        if obj.image:
            from django.utils.html import format_html
            return format_html('<img src="{}" style="height:60px;"/>', obj.image.url)
        return ''
    thumbnail.short_description = 'Image'

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'asset',
        'user',
        'status',
        'start_datetime',
        'end_datetime',
        'received_img',
        'returned_img'
    )
    list_filter = ('asset', 'status')
    search_fields = (
        'user__username',
        'asset__name',
        'contact_name',
        'contact_email',
        'contact_mobile',
        'cancellation_reason'
    )
    readonly_fields = ('received_img', 'returned_img')

    def received_img(self, obj):
        if obj.received_image:
            from django.utils.html import format_html
            return format_html('<a href="{}" target="_blank"><img src="{}" style="height:60px; border-radius:4px;"/></a>', obj.received_image.url, obj.received_image.url)
        return '-'
    received_img.short_description = 'Received Photo'

    def returned_img(self, obj):
        if obj.returned_image:
            from django.utils.html import format_html
            return format_html('<a href="{}" target="_blank"><img src="{}" style="height:60px; border-radius:4px;"/></a>', obj.returned_image.url, obj.returned_image.url)
        return '-'
    returned_img.short_description = 'Returned Photo'

    actions = ['approve_cancellation']

    @admin.action(description='Approve cancellation for selected bookings')
    def approve_cancellation(self, request, queryset):
        for booking in queryset:
            if booking.status == Booking.Status.CANCELLATION_REQUESTED:
                booking.status = Booking.Status.CANCELLED
                booking.save()
        self.message_user(request, "Selected bookings have been cancelled.")

@admin.register(CancellationRequest)
class CancellationRequestAdmin(admin.ModelAdmin):
    list_display = (
        'asset',
        'user',
        'cancellation_reason',
        'start_datetime',
        'end_datetime',
        'status'
    )
    readonly_fields = ('asset', 'user', 'start_datetime', 'end_datetime', 'purpose', 'contact_name', 'contact_email', 'contact_mobile')
    actions = ['approve_cancellation']

    def get_queryset(self, request):
        return super().get_queryset(request).filter(status=Booking.Status.CANCELLATION_REQUESTED)

    @admin.action(description='Approve selected cancellations')
    def approve_cancellation(self, request, queryset):
        for booking in queryset:
            booking.status = Booking.Status.CANCELLED
            booking.save()
        self.message_user(request, "Selected cancellation requests have been approved.")

    def has_add_permission(self, request):
        return False

@admin.register(LocationHistory)
class LocationHistoryAdmin(admin.ModelAdmin):
    list_display = ('asset','location','timestamp')
