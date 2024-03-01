from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse

from .token import account_activation_token


def send_activation_token(user, request):
    # Генерируется абсолютные url с учетом текущего домена и протокола request, токена и идентификатора юзера
    token = account_activation_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    verification_url = reverse("verify_email", kwargs={"uid64": uid, "token": token})
    activation_absolute_url = request.build_absolute_uri(verification_url)

    subject = "Verify email"
    message = f"""Hello {user.username}, please click on the link to verify your account: 
                  {activation_absolute_url}"""
    from_email = 'raevular01@gmail.com'
    recipient_list = [user.email, ]

    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
        fail_silently=False,
    )
