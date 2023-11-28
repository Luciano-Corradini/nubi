from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class RegisterSerializer(serializers.ModelSerializer):
    password_confirmed = serializers.CharField(max_length=128, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password_confirmed', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'password': { 'write_only': True },
            'email': { 'required': True },
            'first_name': { 'required': True },
            'last_name': { 'required': True },
        }

    def validate(self, data):
        password = data['password']
        password_confirmed = data['password_confirmed']

        if password != password_confirmed:
            raise serializers.ValidationError({ "passwords": "Does not match" })

        user_exists = User.objects.filter(email=data['email']).exists()

        if user_exists:
            raise serializers.ValidationError({ 'email': 'already exists' })
        
        return data

    def save(self):
        user = User(
            email=self.validated_data['email'],
            username=self.validated_data['username'],
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
        )
        user.set_password(self.validated_data['password'])
        user.save()

        return user
