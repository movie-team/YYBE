from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        from allauth.account.utils import user_field

        user = super().save_user(request, user, form, False)
        user_field(user, 'nickname', request.data.get('nickname'))
        user.save()
        return user