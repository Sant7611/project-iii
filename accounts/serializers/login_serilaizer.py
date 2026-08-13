from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    class Meta:
        fields = ['email', 'password']
        
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            from django.contrib.auth import authenticate
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            attrs['user']=user
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
        else:
            raise serializers.ValidationError('Both email and password are required.')

        
        return attrs