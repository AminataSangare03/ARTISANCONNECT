from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.accounts.models import Client, User
from apps.artisans.models import Artisan, Realisation
from apps.avis.models import Avis
from apps.commandes.models import Commande
from apps.demandes.models import DemandeService
from apps.devis.models import Devis
from apps.metiers.models import Metier

from .forms import (
    ArtisanProfileUpdateForm,
    AvisForm,
    DemandeServiceForm,
    DevisForm,
    LoginForm,
    RealisationForm,
    RegisterForm,
)


def home_view(request):
    metiers = Metier.objects.filter(is_active=True).annotate(artisans_count=Count('artisans'))[:8]
    featured_artisans = (
        Artisan.objects.filter(user__is_active=True, disponibilite=True)
        .select_related('user', 'metier')
        .prefetch_related('realisations', 'avis_recus')
        .annotate(avg_rating=Avg('avis_recus__note'))
        .order_by('-avg_rating', '-experience')[:6]
    )

    stats = {
        'artisans_count': Artisan.objects.filter(user__is_active=True).count(),
        'metiers_count': Metier.objects.filter(is_active=True).count(),
        'demandes_count': DemandeService.objects.count(),
        'commandes_count': Commande.objects.filter(statut__in=['CONFIRMEE', 'TERMINEE']).count(),
    }

    recent_demandes = (
        DemandeService.objects.filter(statut='EN_ATTENTE')
        .select_related('metier', 'client__user')
        .order_by('-created_at')[:4]
    )

    context = {
        'metiers': metiers,
        'featured_artisans': featured_artisans,
        'stats': stats,
        'recent_demandes': recent_demandes,
    }
    return render(request, 'home.html', context)


def artisan_list_view(request):
    query = request.GET.get('q', '').strip()
    metier_id = request.GET.get('metier', '')
    ville = request.GET.get('ville', '').strip()
    disponible_only = request.GET.get('disponible', '')

    artisans = (
        Artisan.objects.filter(user__is_active=True)
        .select_related('user', 'metier')
        .prefetch_related('realisations', 'avis_recus')
        .annotate(avg_rating=Avg('avis_recus__note'), avis_count=Count('avis_recus'))
    )

    if query:
        artisans = artisans.filter(
            Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(description__icontains=query)
            | Q(metier__nom__icontains=query)
        )
    if metier_id:
        artisans = artisans.filter(metier_id=metier_id)
    if ville:
        artisans = artisans.filter(Q(ville__icontains=ville) | Q(quartier__icontains=ville))
    if disponible_only == '1':
        artisans = artisans.filter(disponibilite=True)

    sort_by = request.GET.get('sort', 'rating')
    if sort_by == 'tarif_asc':
        artisans = artisans.order_by('tarif_indicatif')
    elif sort_by == 'tarif_desc':
        artisans = artisans.order_by('-tarif_indicatif')
    elif sort_by == 'experience':
        artisans = artisans.order_by('-experience')
    else:
        artisans = artisans.order_by('-avg_rating', '-created_at')

    paginator = Paginator(artisans, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    metiers = Metier.objects.filter(is_active=True)
    villes = Artisan.objects.filter(user__is_active=True).values_list('ville', flat=True).distinct()

    context = {
        'page_obj': page_obj,
        'metiers': metiers,
        'villes': [v for v in villes if v],
        'current_q': query,
        'current_metier': metier_id,
        'current_ville': ville,
        'current_disponible': disponible_only,
        'current_sort': sort_by,
    }
    return render(request, 'artisans/list.html', context)


def artisan_detail_view(request, pk):
    artisan = get_object_or_404(
        Artisan.objects.select_related('user', 'metier').prefetch_related('realisations', 'avis_recus__client__user'),
        pk=pk,
        user__is_active=True,
    )
    realisations = artisan.realisations.all()
    avis_list = artisan.avis_recus.all().order_by('-created_at')
    avg_rating = avis_list.aggregate(avg=Avg('note'))['avg'] or 0
    avis_count = avis_list.count()

    context = {
        'artisan': artisan,
        'realisations': realisations,
        'avis_list': avis_list,
        'avg_rating': round(float(avg_rating), 1),
        'avis_count': avis_count,
    }
    return render(request, 'artisans/detail.html', context)


def demande_list_view(request):
    query = request.GET.get('q', '').strip()
    metier_id = request.GET.get('metier', '')
    ville = request.GET.get('ville', '').strip()
    statut = request.GET.get('statut', '')

    demandes = DemandeService.objects.select_related('client__user', 'metier').order_by('-created_at')

    if query:
        demandes = demandes.filter(
            Q(titre__icontains=query)
            | Q(description__icontains=query)
            | Q(ville__icontains=query)
        )
    if metier_id:
        demandes = demandes.filter(metier_id=metier_id)
    if ville:
        demandes = demandes.filter(ville__icontains=ville)
    if statut:
        demandes = demandes.filter(statut=statut)

    paginator = Paginator(demandes, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    metiers = Metier.objects.filter(is_active=True)

    context = {
        'page_obj': page_obj,
        'metiers': metiers,
        'current_q': query,
        'current_metier': metier_id,
        'current_ville': ville,
        'current_statut': statut,
    }
    return render(request, 'demandes/list.html', context)


@login_required
def demande_create_view(request):
    if request.user.role != 'CLIENT' and not request.user.is_superuser:
        messages.error(request, 'Seuls les utilisateurs au profil Client peuvent publier une demande de service.')
        return redirect('demande_list')

    if request.method == 'POST':
        form = DemandeServiceForm(request.POST)
        if form.is_valid():
            client_profile, _ = Client.objects.get_or_create(user=request.user)
            demande = form.save(commit=False)
            demande.client = client_profile
            demande.save()
            messages.success(request, 'Votre demande de service a ete publiee avec succes !')
            return redirect('demande_detail', pk=demande.pk)
    else:
        # Pre-remplir la ville/adresse si le profil client existe
        client_profile = getattr(request.user, 'client_profile', None)
        initial = {}
        if client_profile:
            initial = {
                'ville': client_profile.ville,
                'quartier': client_profile.quartier,
                'adresse': client_profile.adresse,
            }
        # Pre-selection d'un metier si transmis par query param
        pre_metier = request.GET.get('metier')
        if pre_metier:
            initial['metier'] = pre_metier
        form = DemandeServiceForm(initial=initial)

    return render(request, 'demandes/create.html', {'form': form})


def demande_detail_view(request, pk):
    demande = get_object_or_404(
        DemandeService.objects.select_related('client__user', 'metier').prefetch_related('devis__artisan__user'),
        pk=pk,
    )

    is_owner = request.user.is_authenticated and (demande.client.user == request.user or request.user.is_superuser)
    is_matching_artisan = False
    artisan_profile = None
    existing_devis = None

    if request.user.is_authenticated and request.user.role == 'ARTISAN':
        artisan_profile = getattr(request.user, 'artisan_profile', None)
        if artisan_profile and artisan_profile.metier == demande.metier:
            is_matching_artisan = True
            existing_devis = Devis.objects.filter(demande=demande, artisan=artisan_profile).first()

    devis_form = None
    if is_matching_artisan and not existing_devis and demande.statut == 'EN_ATTENTE':
        if request.method == 'POST':
            devis_form = DevisForm(request.POST)
            if devis_form.is_valid():
                devis = devis_form.save(commit=False)
                devis.demande = demande
                devis.artisan = artisan_profile
                devis.save()
                messages.success(request, 'Votre devis a ete soumis au client avec succes !')
                return redirect('demande_detail', pk=demande.pk)
        else:
            devis_form = DevisForm()

    context = {
        'demande': demande,
        'is_owner': is_owner,
        'is_matching_artisan': is_matching_artisan,
        'existing_devis': existing_devis,
        'devis_form': devis_form,
        'devis_list': demande.devis.all() if is_owner else None,
    }
    return render(request, 'demandes/detail.html', context)


@login_required
def devis_action_view(request, pk, action):
    devis = get_object_or_404(Devis.objects.select_related('demande__client__user', 'artisan'), pk=pk)
    if devis.demande.client.user != request.user and not request.user.is_superuser:
        messages.error(request, 'Action non autorisee.')
        return redirect('home')

    if action == 'accepter':
        if devis.demande.statut in ['ACCEPTEE', 'EN_COURS', 'TERMINEE']:
            messages.warning(request, 'Cette demande est deja pourvue.')
        else:
            with transaction.atomic():
                devis.statut = 'ACCEPTE'
                devis.save(update_fields=['statut', 'updated_at'])
                devis.demande.statut = 'ACCEPTEE'
                devis.demande.save(update_fields=['statut', 'updated_at'])
                Devis.objects.filter(demande=devis.demande).exclude(pk=devis.pk).update(statut='REFUSE')
                Commande.objects.get_or_create(
                    devis=devis,
                    defaults={
                        'client': devis.demande.client,
                        'artisan': devis.artisan,
                        'statut': 'EN_ATTENTE',
                    },
                )
            messages.success(request, f'Devis de {devis.artisan} accepte ! La commande est maintenant creee.')
    elif action == 'refuser':
        devis.statut = 'REFUSE'
        devis.save(update_fields=['statut', 'updated_at'])
        messages.info(request, 'Devis refuse.')

    return redirect('demande_detail', pk=devis.demande.pk)


@login_required
def client_dashboard_view(request):
    if request.user.role != 'CLIENT' and not request.user.is_superuser:
        messages.info(request, 'Redirection vers votre espace artisan.')
        return redirect('artisan_dashboard')

    client_profile, _ = Client.objects.get_or_create(user=request.user)
    demandes = DemandeService.objects.filter(client=client_profile).select_related('metier').prefetch_related('devis').order_by('-created_at')
    commandes = Commande.objects.filter(client=client_profile).select_related('artisan__user', 'devis', 'avis').order_by('-created_at')

    # Avis submission
    avis_form = None
    if request.method == 'POST' and 'submit_avis' in request.POST:
        commande_id = request.POST.get('commande_id')
        commande = get_object_or_404(Commande, pk=commande_id, client=client_profile, statut='CONFIRMEE')
        avis_form = AvisForm(request.POST)
        if avis_form.is_valid():
            if not hasattr(commande, 'avis'):
                avis = avis_form.save(commit=False)
                avis.commande = commande
                avis.client = client_profile
                avis.artisan = commande.artisan
                avis.save()
                messages.success(request, 'Votre avis et note ont ete publies avec succes !')
            else:
                messages.warning(request, 'Un avis a deja ete soumis pour cette commande.')
            return redirect('client_dashboard')

    context = {
        'client_profile': client_profile,
        'demandes': demandes,
        'commandes': commandes,
        'avis_form': AvisForm(),
    }
    return render(request, 'dashboard/client.html', context)


@login_required
def artisan_dashboard_view(request):
    if request.user.role != 'ARTISAN' and not request.user.is_superuser:
        messages.info(request, 'Redirection vers votre espace client.')
        return redirect('client_dashboard')

    artisan_profile = getattr(request.user, 'artisan_profile', None)
    if not artisan_profile:
        messages.warning(request, 'Veuillez completer votre profil artisan.')
        return redirect('home')

    matching_demandes = DemandeService.objects.filter(metier=artisan_profile.metier, statut='EN_ATTENTE').select_related('client__user').order_by('-created_at')[:8]
    mes_devis = Devis.objects.filter(artisan=artisan_profile).select_related('demande__client__user').order_by('-created_at')
    commandes = Commande.objects.filter(artisan=artisan_profile).select_related('client__user', 'devis', 'avis').order_by('-created_at')
    realisations = artisan_profile.realisations.all().order_by('-date_realisation')
    avis_recus = artisan_profile.avis_recus.select_related('client__user', 'commande').order_by('-created_at')

    realisation_form = RealisationForm()
    profile_form = ArtisanProfileUpdateForm(instance=artisan_profile)

    if request.method == 'POST':
        if 'add_realisation' in request.POST:
            realisation_form = RealisationForm(request.POST, request.FILES)
            if realisation_form.is_valid():
                real = realisation_form.save(commit=False)
                real.artisan = artisan_profile
                real.save()
                messages.success(request, 'Nouvelle realisation ajoutee a votre portfolio !')
                return redirect('artisan_dashboard')
        elif 'update_profile' in request.POST:
            profile_form = ArtisanProfileUpdateForm(request.POST, request.FILES, instance=artisan_profile)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profil artisan mis a jour avec succes !')
                return redirect('artisan_dashboard')

    context = {
        'artisan': artisan_profile,
        'matching_demandes': matching_demandes,
        'mes_devis': mes_devis,
        'commandes': commandes,
        'realisations': realisations,
        'avis_recus': avis_recus,
        'realisation_form': realisation_form,
        'profile_form': profile_form,
    }
    return render(request, 'dashboard/artisan.html', context)


@login_required
def commande_action_view(request, pk, action):
    commande = get_object_or_404(Commande.objects.select_related('client__user', 'artisan__user'), pk=pk)

    if action == 'demarrer':
        if commande.artisan.user != request.user and not request.user.is_superuser:
            messages.error(request, 'Action reservee a l artisan concerne.')
        else:
            commande.statut = 'EN_COURS'
            commande.date_debut = timezone.now()
            commande.save(update_fields=['statut', 'date_debut', 'updated_at'])
            messages.success(request, 'Prestation declaree en cours.')
        return redirect('artisan_dashboard')

    elif action == 'terminer':
        if commande.artisan.user != request.user and not request.user.is_superuser:
            messages.error(request, 'Action reservee a l artisan concerne.')
        else:
            commande.statut = 'TERMINEE'
            commande.date_fin_reelle = timezone.now()
            commande.save(update_fields=['statut', 'date_fin_reelle', 'updated_at'])
            messages.success(request, 'Prestation marquee comme terminee ! Le client a ete notifie pour confirmation.')
        return redirect('artisan_dashboard')

    elif action == 'confirmer':
        if commande.client.user != request.user and not request.user.is_superuser:
            messages.error(request, 'Action reservee au client concerne.')
        else:
            commande.statut = 'CONFIRMEE'
            commande.save(update_fields=['statut', 'updated_at'])
            messages.success(request, 'Prestation confirmee ! Vous pouvez desormais laisser un avis.')
        return redirect('client_dashboard')

    elif action == 'annuler':
        if commande.client.user != request.user and commande.artisan.user != request.user and not request.user.is_superuser:
            messages.error(request, 'Action non autorisee.')
        elif commande.statut in ['TERMINEE', 'CONFIRMEE']:
            messages.warning(request, 'Une commande achevee ne peut pas etre annulee.')
        else:
            commande.statut = 'ANNULEE'
            commande.save(update_fields=['statut', 'updated_at'])
            messages.info(request, 'Commande annulee.')
        return redirect('client_dashboard' if request.user.role == 'CLIENT' else 'artisan_dashboard')

    return redirect('home')


@login_required
def realisation_delete_view(request, pk):
    realisation = get_object_or_404(Realisation.objects.select_related('artisan__user'), pk=pk)
    if realisation.artisan.user != request.user and not request.user.is_superuser:
        messages.error(request, 'Action non autorisee.')
    else:
        realisation.delete()
        messages.success(request, 'Realisation supprimee avec succes.')
    return redirect('artisan_dashboard')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            messages.success(request, f'Ravi de vous revoir, {user.first_name} !')
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            if user.role == 'ARTISAN':
                return redirect('artisan_dashboard')
            elif user.role == 'CLIENT':
                return redirect('client_dashboard')
            return redirect('home')
    else:
        form = LoginForm()

    return render(request, 'auth/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            with transaction.atomic():
                user = User.objects.create_user(
                    email=data['email'],
                    password=data['password'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    phone_number=data['phone_number'],
                    role=data['role'],
                )
                if data['role'] == 'CLIENT':
                    Client.objects.create(
                        user=user,
                        ville=data['ville'],
                        quartier=data['quartier'],
                        adresse=data['adresse'],
                    )
                elif data['role'] == 'ARTISAN':
                    Artisan.objects.create(
                        user=user,
                        metier=data['metier'],
                        description=data['description'],
                        experience=data['experience'] or 0,
                        ville=data['ville'],
                        quartier=data['quartier'],
                        adresse=data['adresse'],
                        tarif_indicatif=data['tarif_indicatif'] or 0,
                        telephone_professionnel=data['phone_number'],
                        disponibilite=True,
                    )
            login(request, user)
            messages.success(request, f'Bienvenue sur ArtisanConnect, {user.first_name} ! Votre compte a ete cree.')
            if user.role == 'ARTISAN':
                return redirect('artisan_dashboard')
            return redirect('client_dashboard')
    else:
        initial_role = request.GET.get('role', 'CLIENT')
        form = RegisterForm(initial={'role': initial_role})

    return render(request, 'auth/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Vous avez ete deconnecte avec succes.')
    return redirect('home')
