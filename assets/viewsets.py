from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Asset, Booking
from .serializers import AssetSerializer, BookingSerializer
from django.shortcuts import get_object_or_404

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read allowed for any; write only for owners or staff
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user or request.user.is_staff

class AssetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [permissions.AllowAny]

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    from .models import Category
    from .serializers import CategorySerializer
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class SubCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    from .models import SubCategory
    from .serializers import SubCategorySerializer
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = [permissions.AllowAny]

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.select_related('asset','user').all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_permissions(self):
        if self.action in {'accept', 'reject'}:
            return [permissions.IsAdminUser()]
        # Allow cancel for authenticated users (owner check happens in get_queryset or IsOwnerOrReadOnly logic potentially, 
        # but since we use pk lookup on queryset, we need to ensure queryset filters by user appropriately)
        return super().get_permissions()

    def perform_create(self, serializer):
        booking = serializer.save(user=self.request.user)
        if booking.overlaps():
            booking.delete()
            raise serializers.ValidationError('This booking overlaps an existing booking (including the required 1-hour buffer).')
        return booking

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(user=user)

    def _serialize_booking(self, booking):
        serializer = self.get_serializer(booking)
        return serializer.data

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        booking = get_object_or_404(self.get_queryset(), pk=pk)
        if booking.status == Booking.Status.ACCEPTED:
            return Response(self._serialize_booking(booking))
        if booking.status in {Booking.Status.REJECTED, Booking.Status.CANCELLED}:
            return Response({'detail': 'Cannot accept booking in its current status.'}, status=status.HTTP_409_CONFLICT)
        booking.status = Booking.Status.ACCEPTED
        booking.save()
        return Response(self._serialize_booking(booking))

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        booking = get_object_or_404(self.get_queryset(), pk=pk)
        if booking.status == Booking.Status.REJECTED:
            return Response(self._serialize_booking(booking))
        if booking.status == Booking.Status.CANCELLED:
            return Response({'detail': 'Cannot reject booking after cancellation.'}, status=status.HTTP_409_CONFLICT)
        if booking.status == Booking.Status.ACCEPTED:
            return Response({'detail': 'Cannot reject an accepted booking.'}, status=status.HTTP_409_CONFLICT)
        booking.status = Booking.Status.REJECTED
        booking.save()
        return Response(self._serialize_booking(booking))

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = get_object_or_404(self.get_queryset(), pk=pk)
        if booking.status == Booking.Status.CANCELLED:
            return Response(self._serialize_booking(booking))
        if booking.status == Booking.Status.CANCELLATION_REQUESTED:
             return Response(self._serialize_booking(booking))
            
        reason = request.data.get('reason', '')
        booking.status = Booking.Status.CANCELLATION_REQUESTED
        booking.cancellation_reason = reason
        booking.save()
        return Response(self._serialize_booking(booking))

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def cancel_approve(self, request, pk=None):
        booking = get_object_or_404(Booking.objects.all(), pk=pk)
        if booking.status != Booking.Status.CANCELLATION_REQUESTED:
            return Response({'detail': 'Booking is not in cancellation requested state.'}, status=status.HTTP_409_CONFLICT)
        
        booking.status = Booking.Status.CANCELLED
        booking.save()
        return Response(self._serialize_booking(booking))

    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        booking = get_object_or_404(self.get_queryset(), pk=pk)
        if booking.status != Booking.Status.ACCEPTED:
             return Response({'detail': 'Booking must be ACCEPTED to be received.'}, status=status.HTTP_409_CONFLICT)
        
        image = request.FILES.get('image')
        if not image:
            return Response({'detail': 'Image is required.'}, status=status.HTTP_400_BAD_REQUEST)

        from django.utils import timezone
        booking.status = Booking.Status.RECEIVED
        booking.received_image = image
        booking.received_at = timezone.now()
        booking.save()
        return Response(self._serialize_booking(booking))

    @action(detail=True, methods=['post'])
    def return_asset(self, request, pk=None):
        booking = get_object_or_404(self.get_queryset(), pk=pk)
        if booking.status != Booking.Status.RECEIVED:
             return Response({'detail': 'Booking must be RECEIVED to be returned.'}, status=status.HTTP_409_CONFLICT)
        
        image = request.FILES.get('image')
        if not image:
             return Response({'detail': 'Image is required.'}, status=status.HTTP_400_BAD_REQUEST)

        from django.utils import timezone
        booking.status = Booking.Status.RETURNED
        booking.returned_image = image
        booking.returned_at = timezone.now()
        booking.save()
        return Response(self._serialize_booking(booking))
