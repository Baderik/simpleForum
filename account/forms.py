from django import forms

from account.models import User, Profile, FriendRequest

__all__ = ["UserLoginForm", "UserCreationForm", "ProfileForm", "FriendRequestForm"]


class UserLoginForm(forms.Form):
    login = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

    login.widget.attrs["placeholder"] = "Login"
    password.widget.attrs["placeholder"] = "Password"


class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ("login",)

    def clean_password2(self):
        cd = self.cleaned_data
        if cd["password"] != cd["password2"]:
            raise forms.ValidationError("Passwords don't match.")
        return cd["password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ("user", "balance")


class FriendRequestForm(forms.ModelForm):
    class Meta:
        model = FriendRequest
        fields = ("to_user",)
