from django import forms
from django.contrib.auth import authenticate

from apps.accounts.models import Client, User
from apps.artisans.models import Artisan, Realisation
from apps.avis.models import Avis
from apps.demandes.models import DemandeService
from apps.devis.models import Devis
from apps.metiers.models import Metier


class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Adresse email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'exemple@email.com', 'required': True}),
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••', 'required': True}),
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError('Email ou mot de passe incorrect.')
            if not user.is_active:
                raise forms.ValidationError('Ce compte est desactive.')
            cleaned_data['user'] = user
        return cleaned_data


class RegisterForm(forms.Form):
    ROLE_CHOICES = (
        ('CLIENT', 'Je suis un Client (particulier ou entreprise)'),
        ('ARTISAN', 'Je suis un Artisan professionnel'),
    )

    first_name = forms.CharField(
        label='Prenom',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Jean'}),
    )
    last_name = forms.CharField(
        label='Nom de famille',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Kouassi'}),
    )
    email = forms.EmailField(
        label='Adresse email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'exemple@domaine.com'}),
    )
    phone_number = forms.CharField(
        label='Numero de telephone',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 0701020304'}),
    )
    password = forms.CharField(
        label='Mot de passe (8 caracteres min.)',
        min_length=8,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
    )
    confirm_password = forms.CharField(
        label='Confirmer le mot de passe',
        min_length=8,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
    )
    role = forms.ChoiceField(
        label='Type de profil',
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='CLIENT',
    )
    ville = forms.CharField(
        label='Ville',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Abidjan'}),
    )
    quartier = forms.CharField(
        label='Quartier / Commune',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Cocody'}),
    )
    adresse = forms.CharField(
        label='Adresse ou repere',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Pres de la pharmacie...'}),
    )

    # Champs artisan facultatifs au formulaire d inscription
    metier = forms.ModelChoiceField(
        queryset=Metier.objects.filter(is_active=True),
        label='Metier (requis si artisan)',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    tarif_indicatif = forms.DecimalField(
        label='Tarif indicatif journalier (FCFA)',
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 25000'}),
    )
    experience = forms.IntegerField(
        label='Annees d experience',
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 5'}),
    )
    description = forms.CharField(
        label='Description de vos competences (si artisan)',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Decrivez vos specialites et atouts...'}),
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Cette adresse email est deja utilisee.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        role = cleaned_data.get('role')
        metier = cleaned_data.get('metier')

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Les mots de passe ne correspondent pas.')

        if role == 'ARTISAN' and not metier:
            raise forms.ValidationError('Veuillez selectionner un metier pour le compte artisan.')

        return cleaned_data


class DemandeServiceForm(forms.ModelForm):
    class Meta:
        model = DemandeService
        fields = ('metier', 'titre', 'description', 'ville', 'quartier', 'adresse', 'budget_indicatif', 'date_souhaitee')
        widgets = {
            'metier': forms.Select(attrs={'class': 'form-select'}),
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Fuite sous lavabo et robinet cassé'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Donnez tous les details pertinents sur votre besoin...'}),
            'ville': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Abidjan'}),
            'quartier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Marcory Zone 4'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Rue des Majorettes, Villa 4'}),
            'budget_indicatif': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 35000'}),
            'date_souhaitee': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class DevisForm(forms.ModelForm):
    class Meta:
        model = Devis
        fields = ('montant', 'duree_estimee', 'validite', 'description')
        widgets = {
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Montant propose en FCFA'}),
            'duree_estimee': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 2 jours ouvrables'}),
            'validite': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Details de l intervention, fournitures incluses...'}),
        }


class AvisForm(forms.ModelForm):
    NOTE_CHOICES = [(i, f'{i} etoile{"s" if i > 1 else ""}') for i in range(5, 0, -1)]
    note = forms.ChoiceField(
        choices=NOTE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Note sur 5',
    )

    class Meta:
        model = Avis
        fields = ('note', 'commentaire')
        widgets = {
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Partagez votre retour d experience sur la prestation...'}),
        }


class RealisationForm(forms.ModelForm):
    class Meta:
        model = Realisation
        fields = ('titre', 'description', 'image')
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de la realisation'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description des travaux effectues...'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class ArtisanProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Artisan
        fields = ('metier', 'description', 'experience', 'ville', 'quartier', 'adresse', 'disponibilite', 'tarif_indicatif', 'telephone_professionnel', 'photo_profil')
        widgets = {
            'metier': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'experience': forms.NumberInput(attrs={'class': 'form-control'}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'quartier': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'disponibilite': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tarif_indicatif': forms.NumberInput(attrs={'class': 'form-control'}),
            'telephone_professionnel': forms.TextInput(attrs={'class': 'form-control'}),
            'photo_profil': forms.FileInput(attrs={'class': 'form-control'}),
        }
