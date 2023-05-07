from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    """
    Менеджер для создания пользователей по эл. почте
    """

    use_in_migrations = True

    def create_user(self, email, password, **extra_fields):
        """
        Создание пользователя с паролем и эл. почтой
        """
        if not email:
            # email является обязательным, что что кидаем ошибку, если не указан
            raise ValueError('Необходимо указать электронную почту')
        email = self.normalize_email(email)
        # создаем экземпляр пользователя
        user = self.model(email=email, **extra_fields)
        # устанавливаем пароль
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Создание супер-пользователя с паролем и эл. почтой
        """
        # определим админским полям значения по умолчанию
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        # если убрали флаг админа или суперюзера, то кидаем ошибки
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен быть членом персонала')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен быть отмечен как суперпользователь')

        # когда убедились, что у всех полей правильные значения, вызываем метод создания пользователя
        return self.create_user(email, password, **extra_fields)
