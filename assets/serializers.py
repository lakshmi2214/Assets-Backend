from rest_framework import serializers
from .models import Asset, Booking, Location, Category, SubCategory
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username')

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id','name','description')

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ('id', 'name', 'category')

class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'subcategories')

class AssetSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(write_only=True, source='category', queryset=Category.objects.all(), allow_null=True)
    subcategory = SubCategorySerializer(read_only=True)
    subcategory_id = serializers.PrimaryKeyRelatedField(write_only=True, source='subcategory', queryset=SubCategory.objects.all(), allow_null=True)
    image_url = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = Asset
        fields = ('id','name','description','details','serial_number','location','category','category_id','subcategory','subcategory_id','available','total_quantity','image','image_url', 'status')
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        storage_cls = type(obj.image.storage).__name__
        if obj.image:
            return f"DEPLOYMENT_TEST: {storage_cls} :: " + str(obj.image.url)
        return None

    def get_status(self, obj):
        if not obj.available:
            return 'Out of Stock'
        
        from django.utils import timezone
        from django.db.models import Sum
        now = timezone.now()
        
        # Current booked quantity at this exact moment
        booked_qty = obj.bookings.filter(
            start_datetime__lte=now, 
            end_datetime__gte=now,
            status__in=['accepted', 'received']
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        if booked_qty >= obj.total_quantity:
            return 'Out of Stock'
            
        remaining = obj.total_quantity - booked_qty
        return f'{remaining} Units Available'

class BookingSerializer(serializers.ModelSerializer):
    asset = AssetSerializer(read_only=True)
    asset_id = serializers.PrimaryKeyRelatedField(write_only=True, source='asset', queryset=Asset.objects.all())
    user = UserSerializer(read_only=True)
    contact_location = LocationSerializer(read_only=True)
    contact_location_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source='contact_location',
        queryset=Location.objects.all(),
        allow_null=True,
        required=False
    )

    class Meta:
        model = Booking
        fields = (
            'id',
            'asset',
            'asset_id',
            'user',
            'quantity',
            'start_datetime',
            'end_datetime',
            'purpose',
            'contact_name',
            'contact_email',
            'contact_mobile',
            'contact_address',
            'contact_location',
            'contact_location_id',
            'created_at',
            'status',
            'received_image',
            'received_at',
            'returned_image',
            'returned_at'
        )
        read_only_fields = ('status', 'received_at', 'returned_at')

    def validate(self, data):
        start = data.get('start_datetime') or getattr(self.instance, 'start_datetime', None)
        end = data.get('end_datetime') or getattr(self.instance, 'end_datetime', None)
        qty = data.get('quantity') or getattr(self.instance, 'quantity', 1)
        asset = data.get('asset') or getattr(self.instance, 'asset', None)

        if start and end and start >= end:
            raise serializers.ValidationError('End must be after start.')
        
        from django.utils import timezone
        # If this is a new booking (no instance) or start time is being changed
        if not self.instance and start and start < timezone.now():
             raise serializers.ValidationError({"start_datetime": "Booking start time cannot be in the past."})
        
        if asset and qty > asset.total_quantity:
            raise serializers.ValidationError({"quantity": f"Only {asset.total_quantity} units available for this asset."})
        
        # Use models' overlap logic
        mock_booking = Booking(
            asset=asset,
            start_datetime=start,
            end_datetime=end,
            quantity=qty,
            pk=self.instance.pk if self.instance else None
        )
        if mock_booking.overlaps():
            raise serializers.ValidationError("Booking overlaps with existing reservations. Try a different time or reduce quantity.")

        return data
