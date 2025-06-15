from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)

        if sociallogin.account.provider == 'google':            
            email = sociallogin.account.extra_data.get('email')
            if email and not user.email:
                user.email = email

        return user

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)

        if sociallogin.account.provider == 'google':
            email = sociallogin.account.extra_data.get('email')
            if email:
                user.email = email

        return user