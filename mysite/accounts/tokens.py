from django.contrib.auth.tokens import PasswordResetTokenGenerator

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # Це додаємо для того, щоб токен став недійсним після зміни паролю.
        login_timestamp = '' if user.last_login is None else user.last_login.replace(microsecond=0, tzinfo=None)
        return (
            str(user.pk) + str(timestamp) +
            str(user.is_active) + str(login_timestamp)
        )

account_activation_token = AccountActivationTokenGenerator()
