from rest_framework import serializers
from .models import User
from django.utils import timezone 


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [ 'name', 'email', 'password', 'country',  'city', 'is_verified', 'verified_dateTime', 'email_verify_token', 'email_verify_token_dateTime', 'forgot_password_token', 'forgot_password_token_dateTime']
        extra_kwargs = {
            'password': {'write_only':True}
        }
        
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is  not None:
            instance.set_password(password)
        instance.save()
        return instance



# class LoginUsersSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = LogInUsers
#         fields = '__all__'

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'country', 'city']  

class PasswordUpdateSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()