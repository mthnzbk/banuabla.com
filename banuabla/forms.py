from django import forms
from banuabla.models import User


class ProfileForm(forms.Form):
    first_name = forms.CharField(max_length=50, label="Adın", required=False,
                                 widget=forms.TextInput(attrs={"class": "validate", "data-length": "50"}))
    last_name = forms.CharField(max_length=50, label="Soyadın", required=False,
                                widget=forms.TextInput(attrs={"class": "validate", "data-length": "50"}))
    birth = forms.IntegerField(label="Doğum Yılın", required=False, max_value=2018, min_value=1900,
                               widget=forms.NumberInput(attrs={"class": "validate", "data-length": "4"}))
    gender = forms.CharField(label="Cinsiyetin", required=False, widget=forms.Select(attrs={"class": "validate",
                                                                                            "data-length": "50"},
                                                                                     choices=User.cinsiyet))
    about = forms.CharField(max_length=500, label="Hakkınızda", label_suffix="", required=False,
                            widget=forms.Textarea(attrs={"class": "materialize-textarea", "data-length": "500"}))
    password = forms.CharField(max_length=50, label="Parola", required=False, min_length=6,
                               widget=forms.PasswordInput(attrs={"class": "validate", "data-length": "50"}))
    password2 = forms.CharField(max_length=50, label="Parola (tekrar)", required=False, min_length=6,
                                widget=forms.PasswordInput(attrs={"class": "validate", "data-length": "50"}))


class UploadForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ("user_photo",)


class ForgotpasswdForm(forms.Form):
    forgot_email = forms.EmailField(max_length=50, label="E-Posta", label_suffix="",
                                    widget=forms.EmailInput(attrs={"class": "validate", "data-length": "50"}))


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=50, label="E-Posta", label_suffix="",
                            widget=forms.EmailInput(attrs={"class": "validate", "data-length": "50"}))
    password = forms.CharField(max_length=50, label="Parola", label_suffix="",
                               widget=forms.PasswordInput(attrs={"class": "validate", "data-length": "50"}))


class RegisterForm(forms.Form):
    user_email = forms.EmailField(max_length=50, label="E-Posta", label_suffix="", required=True,
                             widget=forms.EmailInput(attrs={"class": "validate", "data-length": "50"}))
    user_password = forms.CharField(max_length=50, min_length=6, label="Parola", label_suffix="",
                               widget=forms.PasswordInput(attrs={"class": "validate", "data-length": "50"}))
    user_password2 = forms.CharField(max_length=50, min_length=6, label="Parola (tekrar)", label_suffix="",
                                widget=forms.PasswordInput(attrs={"class": "validate", "data-length": "50"}))


class ContactForm(forms.Form):
    full_name = forms.CharField(max_length=50, label="Ad Soyad", label_suffix="",
                                widget=forms.TextInput(attrs={"class": "validate", "data-length": "50"}))

    guest_email = forms.EmailField(max_length=50, label="E-Posta", label_suffix="",
                             widget=forms.EmailInput(attrs={"class": "validate", "data-length": "50"}))

    subject = forms.CharField(max_length=50, label="Konu", label_suffix="",
                                widget=forms.TextInput(attrs={"class": "validate", "data-length": "50"}))

    message = forms.CharField(max_length=500, label="Mesajınız", label_suffix="",
                              widget=forms.Textarea(attrs={"class": "materialize-textarea", "data-length": "500"}))


class OrderAddForm(forms.Form):
    fal1 = forms.ImageField(required=False)
    fal2 = forms.ImageField(required=False)
    fal3 = forms.ImageField(required=False)
    fal4 = forms.ImageField(required=False)
    message = forms.CharField(widget=forms.Textarea(attrs={"class": "materialize-textarea", "data-length": "500"}),
                              required=False, label="Mesajınız", label_suffix="", max_length=500)


class OrderMessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(attrs={"class": "materialize-textarea", "data-length": "500"}),
                              max_length=500, label="Mesajınız", label_suffix="", required=False)
    sound = forms.FileField(required=False, label_suffix="", label="Fal Yorumu")



