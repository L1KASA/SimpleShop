from django.conf import settings
from django.contrib import messages

import requests


def check_recaptcha(function):
    def wrap(request, *args, **kwargs):
        request.recaptcha_is_valid = None
        if request.method == 'POST':
            recaptcha_response = request.POST.get('g-recaptcha-response')
            data = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            try:
                response = requests.post(
                    'https://www.google.com/recaptcha/api/siteverify',
                    data=data,
                    timeout=settings.GOOGLE_RECAPTCHA_TIMEOUT
                )
                result = response.json()

                if result['success']:
                    request.recaptcha_is_valid = True
                else:
                    request.recaptcha_is_valid = False
                    messages.error(request, 'Invalid reCAPTCHA. Please try again.')
            except requests.exceptions.Timeout:
                request.recaptcha_is_valid = False
                messages.error(request, 'reCAPTCHA verification timeout. Please try again.')
            except requests.exceptions.ConnectionError:
                request.recaptcha_is_valid = False
                messages.error(
                    request,
                   'Connection error during reCAPTCHA verification. Please check your internet connection.'
                )
            except requests.exceptions.RequestException as e:
                request.recaptcha_is_valid = False
                messages.error(
                    request,
                    'Network error occurred during reCAPTCHA verification. Please try again later.'
                )
            except ValueError:
                request.recaptcha_is_valid = False
                messages.error(
                    request,
                    'Invalid response from reCAPTCHA service. Please try again.'
                )
            except Exception as e:
                request.recaptcha_is_valid = False
                messages.error(
                    request,
                    'An unexpected error occurred during reCAPTCHA verification. Please try again.'
                )
        return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
