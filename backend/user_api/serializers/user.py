from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from user_api.utils.creating_email_message import send_confirmation_email
from user_api.utils.token_generator import create_confirmation_token
from user_api.validations import custom_validate_email, validate_password
from users.models import EmailConfirmationToken

UserModel = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['email',
                  # 'username',
                  'last_name', 'first_name',
                  'patronymic', 'password', ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = UserModel(**validated_data)
        user.is_active = False
        user.set_password(password)
        user.save()
        self.send_confirmation_email(user)
        return user

    def send_confirmation_email(self, user):
        existing_token = EmailConfirmationToken.objects.filter(user=user).first()
        if existing_token:
            raise ValidationError("Токен уже существует для данного пользователя")

        confirmation_token = create_confirmation_token(user)
        send_confirmation_email(user, confirmation_token)

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Пароль должен быть больше 8 символов")
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Пароль должен содержать хотя бы одну цифру")
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError("Пароль должен содержать хотя бы одну букву")
        return value


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def check_user(self, clean_data):
        user = authenticate(email=clean_data['email'], password=clean_data['password'])
        if not user:
            raise serializers.ValidationError('Email or password is incorrect')
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('email', 'username', 'last_name', 'first_name', 'patronymic')


class UserWithIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('id', 'email', 'username', 'last_name', 'first_name',)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, data):
        request = self.context.get('request')
        user = request.user if request else None

        if not user:
            raise serializers.ValidationError("Вы не зашли в аккаунт.")

        if not user.check_password(data.get('old_password')):
            raise serializers.ValidationError({"old_password": "Неправильный пароль."})

        old_password = data.get('old_password')
        new_password = data.get('new_password')

        # Проверка правильности старого пароля
        if not user.check_password(old_password):
            raise serializers.ValidationError({"old_password": "Неверный старый пароль."})

        # Использование функции validate_password для проверки нового пароля
        try:
            validate_password(new_password)
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": str(e)})

        return data

    def save(self, **kwargs):
        request = self.context.get('request')
        user = request.user if request else None
        user.password = make_password(self.validated_data['new_password'])
        user.save()
        return user


class ChangeNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['first_name', 'last_name', 'patronymic', ]

    def validate_first_name(self, value):
        if not value:
            raise serializers.ValidationError("Имя не может быть пустым.")
        if not value.isalpha():
            raise serializers.ValidationError("Имя должно содержать только буквы.")
        return value

    def validate_last_name(self, value):
        if not value:
            raise serializers.ValidationError("Фамилия не может быть пустой.")
        if not value.isalpha():
            raise serializers.ValidationError("Фамилия должна содержать только буквы.")
        return value

    def validate_patronymic(self, value):
        return value

    def validate(self, data):
        return data

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.patronymic = validated_data.get('patronymic', instance.patronymic)
        instance.save()
        return instance


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class UserChangeEmailSerializer(serializers.Serializer):
    new_email = serializers.EmailField()  # Поле для нового email
    password = serializers.CharField(write_only=True)  # Поле для пароля

    def validate(self, data):
        request = self.context.get('request')
        user = request.user if request else None

        if not user:
            raise ValidationError("Пользователь не вошёл в систему.")

        if not user.check_password(data.get('password')):
            raise ValidationError({"password": "Неправильный пароль."})

        new_email = data.get('new_email')

        if user.email == new_email:
            raise ValidationError({'new_email': 'Новая почта не может быть такая же, как старая.'})

        try:
            custom_validate_email(new_email)
        except ValidationError as e:
            raise serializers.ValidationError({"email": str(e)})

        return data


class UserTryChangePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        """
        Проверяем, существует ли пользователь с данным email.
        """
        try:
            user = UserModel.objects.get(email=value)
        except UserModel.DoesNotExist:
            raise serializers.ValidationError("Пользователь с таким email не найден.")
        return value

