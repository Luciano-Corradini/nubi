from rest_framework import serializers
from customer import models


class CustomerUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    name = serializers.CharField(required=False, max_length=50)
    last_name = serializers.CharField(required=False, max_length=50)

    class Meta:
        model = models.CustomerUser
        fields = ('email', 'name', 'last_name')
    
    def validate(self, data):
        request = self.context['request']
        
        if request.method == 'POST':
            errors = {}

            if 'email' not in data:
                errors['email'] = 'This field is required.'
            if 'name' not in data:
                errors['name'] = 'This field is required.'
            if 'last_name' not in data:
                errors['last_name'] = 'This field is required.'

            if errors:
                raise serializers.ValidationError(errors)

            email = data['email']

            if models.CustomerUser.objects.filter(email=email).exists():
                raise serializers.ValidationError({'user': {'email': 'user with this dni already exists.'}})

        if request.method == 'PUT':
            email = data.get('email')
            qs = models.CustomerUser.objects.filter(email=email)

            if email and qs.exists():
                raise serializers.ValidationError({'user': {'email': 'user with this dni already exists.'}})

        return data


class CustomerSerializer(serializers.ModelSerializer):
    user = CustomerUserSerializer()
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = models.Customer
        fields = ('wallet_id', 'sex_tape', 'dni', 'birth_date', 'created_at', 'user')

    def create(self, validated_data):
        user_data = validated_data.pop('user', {})
        user = models.CustomerUser.objects.create(**user_data)
        customer = models.Customer.objects.create(user=user, **validated_data)
        return customer

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user

        for key, value in user_data.items():
            setattr(user, key, value)
        user.save(update_fields=user_data.keys())

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save(update_fields=validated_data.keys())

        instance.refresh_from_db()

        return instance
