from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from customer.models import Customer
from customer.serializers import CustomerSerializer
from customer.pagination import CustomerListPagination

class CustomerRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer(self, *args, **kwargs):
        kwargs['partial'] = True
        return super().get_serializer(*args, **kwargs)

class CustomerListCreateView(ListCreateAPIView):
    pagination_class = CustomerListPagination
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['wallet_id', 'dni', 'user__email']
    ordering = ['created_at']
    filterset_fields = {
        'wallet_id': ['exact'],
        'dni': ['exact'],
        'user__email': ['exact'],
    }

    def get_serializer(self, *args, **kwargs):
        kwargs['partial'] = False
        return super().get_serializer(*args, **kwargs)
