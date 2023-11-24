from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from customer.models import Customer
from customer.serializers import CustomerSerializer
from customer.pagination import CustomerListPagination

class CustomerRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def get_serializer(self, *args, **kwargs):
        kwargs['partial'] = True
        return super().get_serializer(*args, **kwargs)

class CustomerListCreateView(ListCreateAPIView):
    pagination_class = CustomerListPagination
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    filter_backends = [OrderingFilter, DjangoFilterBackend]
    ordering_fields = '__all__'
    ordering = ['created_at']
    filterset_fields = {
        "wallet_id": ['exact'],
        "sex_tape": ['exact'],
        "dni": ['exact'],
        "birth_date": ['exact', 'gte', 'lte'],
        "created_at": ['exact', 'gte', 'lte'],
        'user__email': ['exact'],
        'user__name': ['exact'],
        'user__last_name': ['exact'],
    }

    def get_serializer(self, *args, **kwargs):
        kwargs['partial'] = False
        return super().get_serializer(*args, **kwargs)
