from django.contrib.auth.tokens import PasswordResetTokenGenerator


class MyActivationTokenGenerator(PasswordResetTokenGenerator):
    # Генератор токена для активации
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(user.password) + str(timestamp)


account_activation_token = MyActivationTokenGenerator()
