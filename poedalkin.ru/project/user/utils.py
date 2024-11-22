from .models import SessionOAuth
from shop.models import Basket

def get_user(request):

    access_token = request.headers.get("Authorization")
    session = SessionOAuth.objects.filter(access_token=access_token).first()

    if session:
        session.update_token_by_status()

    session = SessionOAuth.objects.filter(access_token=access_token).first()

    if(not session):
        raise SessionOAuth.UserNotFound()

    if(not session.is_active):
        raise SessionOAuth.TokenWasExpires()
        
    else:
        return session.user

def get_basket(user):
    try:
        return user.basket
    except Basket.DoesNotExist:
        basket = Basket(user=user)
        basket.save()
        return basket

def is_valid_password(string):
    numbers_chr = [chr(x) for x in range(48, 58)]
    uppercases_chr = [chr(x) for x in range(65, 91)]
    downcases_chr = [chr(x) for x in range(97, 122)]

    for letter in string:
        if not letter in numbers_chr and not letter in uppercases_chr and not letter in downcases_chr:
            return False

    return True

def is_hard_password(string):
    uppercases = 0
    downcases = 0 
    numbers = 0

    numbers_chr = [chr(x) for x in range(48, 58)]
    uppercases_chr = [chr(x) for x in range(65, 91)]
    downcases_chr = [chr(x) for x in range(97, 122)]

    for letter in string:
        if(letter in numbers_chr):
            numbers += 1
            continue
        if(letter in uppercases_chr):
            uppercases += 1
            continue
        if(letter in downcases_chr):
            downcases += 1
            continue

    if(uppercases >= 4 and downcases >= 4 and numbers >= 2):
        return True
    else:
        return False