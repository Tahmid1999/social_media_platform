from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
import jwt
from user.models import User  


def authenticate_user(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        raise AuthenticationFailed('Authentication credentials were not provided.')

    try:
        token = auth_header.split(' ')[1]
    except IndexError:
        raise AuthenticationFailed('Invalid token format')

    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token has expired.')
    except jwt.DecodeError:
        raise AuthenticationFailed('Token is invalid.')

    user = User.objects.filter(_id=payload['id']).first()
    if user is None:
        raise AuthenticationFailed('Token is invalid.')

    token_found = False
    for token_entry in user.logged_in_tokens:
        if token_entry['token'] == token:
            token_found = True
            break

    if not token_found:
        raise AuthenticationFailed('Token is invalid.')

    return user
