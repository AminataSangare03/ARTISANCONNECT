from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Avg, Count, Prefetch, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

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

COMMANDE_STEPS = [
    ('EN_ATTENTE', 'Commande créée'),
    ('EN_COURS', 'Travaux en cours'),
    ('TERMINEE', 'Travaux terminés'),
    ('CONFIRMEE', 'Validée par le client'),
]


def _rated_artisans():
    """Artisans actifs annotes avec leur note moyenne et leur nombre d'avis."""
    return (
        Artisan.objects.filter(user__is_active=True)
        .select_related('user', 'metier')
        .prefetch_related('realisations')
        .annotate(avg_rating=Avg('avis_recus__note'), avis_count=Count('avis_recus', distinct=True))
    )


def _attach_steps(commandes):
    """Ajoute a chaque commande la liste des etapes de suivi (pour la frise)."""
    order = [code for code, _ in COMMANDE_STEPS]
    for commande in commandes:
        current = order.index(commande.statut) if commande.statut in order else -1
        commande.steps = [
            {'label': label, 'done': idx <= current, 'current': idx == current}
            for idx, (_, label) in enumerate(COMMANDE_STEPS)
        ]
    return commandes


def _redirect_back(request, fallback):
    target = request.POST.get('next') or request.META.get('HTTP_REFERER')
    if target and url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return redirect(target)
    return redirect(fallback)


# ---------------------------------------------------------------------------
# Pages publiques
# ---------------------------------------------------------------------------

def home_view(request):
    metiers = (
        Metier.objects.filter(is_active=True)
        .annotate(artisans_count=Count('artisans', filter=Q(artisans__user__is_active=True)))
        .order_by('-artisans_count', 'nom')[:7]
    )
    featured_artisans = _rated_artisans().filter(disponibilite=True).order_by('-avg_rating', '-experience')[:4]
    recent_demandes = (
        DemandeService.objects.filter(statut='EN_ATTENTE')
        .select_related('metier', 'client__user')
        .annotate(devis_count=Count('devis'))
        .order_by('-created_at')[:4]
    )
    temoignages = Avis.objects.select_related('client__user', 'artisan__user', 'artisan__metier').filter(note__gte=4).order_by('-created_at')[:3]

    stats = {
        'artisans_count': Artisan.objects.filter(user__is_active=True).count(),
        'metiers_count': Metier.objects.filter(is_active=True).count(),
        'demandes_count': DemandeService.objects.count(),
        'commandes_count': Commande.objects.filter(statut='CONFIRMEE').count(),
        'note_moyenne': Avis.objects.aggregate(avg=Avg('note'))['avg'],
    }

    return render(request, 'home.html', {
        'metiers': metiers,
        'all_metiers': Metier.objects.filter(is_active=True),
        'featured_artisans': featured_artisans,
        'recent_demandes': recent_demandes,
        'temoignages': temoignages,
        'stats': stats,
    })


def artisan_list_view(request):
    query = request.GET.get('q', '').strip()
    metier_id = request.GET.get('metier', '').strip()
    ville = request.GET.get('ville', '').strip()
    disponible_only = request.GET.get('disponible', '')
    sort_by = request.GET.get('sort', 'rating')

    artisans = _rated_artisans()
    if query:
        artisans = artisans.filter(
            Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(description__icontains=query)
            | Q(metier__nom__icontains=query)
        )
    if metier_id.isdigit():
        artisans = artisans.filter(metier_id=metier_id)
    if ville:
        artisans = artisans.filter(Q(ville__icontains=ville) | Q(quartier__icontains=ville))
    if disponible_only == '1':
        artisans = artisans.filter(disponibilite=True)

    ordering = {
        'tarif_asc': ('tarif_indicatif',),
        'tarif_desc': ('-tarif_indicatif',),
        'experience': ('-experience',),
    }.get(sort_by, ('-avg_rating', '-avis_count', '-experience'))
    artisans = artisans.order_by(*ordering)

    page_obj = Paginator(artisans, 9).get_page(request.GET.get('page'))
    params = request.GET.copy()
    params.pop('page', None)

    return render(request, 'artisans/list.html', {
        'page_obj': page_obj,
        'metiers': Metier.objects.filter(is_active=True),
        'current_q': query,
        'current_metier': metier_id,
        'current_ville': ville,
        'current_disponible': disponible_only,
        'current_sort': sort_by,
        'querystring': params.urlencode(),
        'selected_metier': Metier.objects.filter(pk=metier_id).first() if metier_id.isdigit() else None,
    })


def artisan_detail_view(request, pk):
    artisan = get_object_or_404(
        Artisan.objects.select_related('user', 'metier').prefetch_related(
            'realisations',
            Prefetch('avis_recus', queryset=Avis.objects.select_related('client__user').order_by('-created_at')),
        ),
        pk=pk,
        user__is_active=True,
    )
    avis_list = list(artisan.avis_recus.all())
    avis_count = len(avis_list)
    avg_rating = (sum(a.note for a in avis_list) / avis_count) if avis_count else None
    distribution = []
    for note in range(5, 0, -1):
        count = sum(1 for a in avis_list if a.note == note)
        distribution.append({'note': note, 'count': count, 'pct': round(count * 100 / avis_count) if avis_count else 0})

    similaires = _rated_artisans().filter(metier=artisan.metier).exclude(pk=artisan.pk).order_by('-avg_rating')[:3]

    return render(request, 'artisans/detail.html', {
        'artisan': artisan,
        'realisations': artisan.realisations.all(),
        'avis_list': avis_list,
        'avg_rating': avg_rating,
        'avis_count': avis_count,
        'distribution': distribution,
        'similaires': similaires,
        'commandes_terminees': Commande.objects.filter(artisan=artisan, statut='CONFIRMEE').count(),
    })


def demande_list_view(request):
    query = request.GET.get('q', '').strip()
    metier_id = request.GET.get('metier', '').strip()
    ville = request.GET.get('ville', '').strip()
    statut = request.GET.get('statut', 'EN_ATTENTE')

    demandes = (
        DemandeService.objects.select_related('client__user', 'metier')
        .annotate(devis_count=Count('devis'))
        .order_by('-created_at')
    )
    if query:
        demandes = demandes.filter(Q(titre__icontains=query) | Q(description__icontains=query))
    if metier_id.isdigit():
        demandes = demandes.filter(metier_id=metier_id)
    if ville:
        demandes = demandes.filter(Q(ville__icontains=ville) | Q(quartier__icontains=ville))
    if statut and statut != 'TOUS':
        demandes = demandes.filter(statut=statut)

    page_obj = Paginator(demandes, 8).get_page(request.GET.get('page'))
    params = request.GET.copy()
    params.pop('page', None)

    return render(request, 'demandes/list.html', {
        'page_obj': page_obj,
        'metiers': Metier.objects.filter(is_active=True),
        'statuts': DemandeService.STATUS_CHOICES,
        'current_q': query,
        'current_metier': metier_id,
        'current_ville': ville,
        'current_statut': statut,
        'querystring': params.urlencode(),
    })


def demande_detail_view(request, pk):
    demande = get_object_or_404(
        DemandeService.objects.select_related('client__user', 'metier').prefetch_related(
            Prefetch('devis', queryset=Devis.objects.select_related('artisan__user', 'artisan__metier').order_by('montant'))
        ),
        pk=pk,
    )
    user = request.user
    is_owner = user.is_authenticated and (demande.client.user_id == user.id or user.is_superuser)
    artisan_profile = getattr(user, 'artisan_profile', None) if user.is_authenticated and user.role == 'ARTISAN' else None
    is_matching_artisan = bool(artisan_profile and artisan_profile.metier_id == demande.metier_id)
    existing_devis = Devis.objects.filter(demande=demande, artisan=artisan_profile).first() if is_matching_artisan else None

    devis_form = None
    if is_matching_artisan and not existing_devis and demande.statut == 'EN_ATTENTE':
        devis_form = DevisForm(request.POST or None)
        if request.method == 'POST' and devis_form.is_valid():
            devis = devis_form.save(commit=False)
            devis.demande = demande
            devis.artisan = artisan_profile
            devis.save()
            messages.success(request, 'Votre devis a été envoyé au client. Vous serez informé de sa décision.')
            return redirect('demande_detail', pk=demande.pk)

    return render(request, 'demandes/detail.html', {
        'demande': demande,
        'is_owner': is_owner,
        'is_matching_artisan': is_matching_artisan,
        'existing_devis': existing_devis,
        'devis_form': devis_form,
        'devis_list': demande.devis.all() if is_owner else None,
        'devis_count': demande.devis.count(),
    })


# ---------------------------------------------------------------------------
# Actions client
# ---------------------------------------------------------------------------

@login_required
def demande_create_view(request):
    if request.user.role != 'CLIENT':
        messages.error(request, 'La publication de demandes est réservée aux comptes client.')
        return redirect('demande_list')

    client_profile, _ = Client.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = DemandeServiceForm(request.POST)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.client = client_profile
            demande.save()
            messages.success(request, 'Votre demande est publiée. Les artisans du métier peuvent maintenant vous envoyer leurs devis.')
            return redirect('demande_detail', pk=demande.pk)
    else:
        initial = {'ville': client_profile.ville or 'Bamako', 'quartier': client_profile.quartier, 'adresse': client_profile.adresse}
        if request.GET.get('metier', '').isdigit():
            initial['metier'] = request.GET['metier']
        form = DemandeServiceForm(initial=initial)

    return render(request, 'demandes/create.html', {'form': form})


@login_required
@require_POST
def devis_action_view(request, pk, action):
    devis = get_object_or_404(Devis.objects.select_related('demande__client__user', 'artisan__user'), pk=pk)
    if devis.demande.client.user_id != request.user.id:
        messages.error(request, 'Seul le client ayant publié la demande peut répondre à ce devis.')
        return redirect('home')

    if devis.statut != 'EN_ATTENTE':
        messages.warning(request, 'Ce devis a déjà été traité.')
    elif action == 'accepter':
        if devis.demande.statut != 'EN_ATTENTE':
            messages.warning(request, 'Un devis a déjà été accepté pour cette demande.')
        elif devis.validite and devis.validite < timezone.localdate():
            devis.statut = 'EXPIRE'
            devis.save(update_fields=['statut', 'updated_at'])
            messages.warning(request, 'Ce devis a expiré et ne peut plus être accepté.')
        else:
            with transaction.atomic():
                devis.statut = 'ACCEPTE'
                devis.save(update_fields=['statut', 'updated_at'])
                devis.demande.statut = 'ACCEPTEE'
                devis.demande.save(update_fields=['statut', 'updated_at'])
                Devis.objects.filter(demande=devis.demande, statut='EN_ATTENTE').exclude(pk=devis.pk).update(statut='REFUSE')
                Commande.objects.get_or_create(
                    devis=devis,
                    defaults={'client': devis.demande.client, 'artisan': devis.artisan, 'statut': 'EN_ATTENTE'},
                )
            messages.success(request, f'Devis de {devis.artisan} accepté. La commande est créée et suivie dans votre espace.')
            return redirect('client_dashboard')
    elif action == 'refuser':
        devis.statut = 'REFUSE'
        devis.save(update_fields=['statut', 'updated_at'])
        messages.info(request, 'Devis refusé.')
    else:
        messages.error(request, 'Action inconnue.')

    return redirect('demande_detail', pk=devis.demande.pk)


@login_required
def client_dashboard_view(request):
    if request.user.role == 'ARTISAN':
        return redirect('artisan_dashboard')
    if request.user.role != 'CLIENT':
        messages.info(request, 'Les administrateurs gèrent la plateforme depuis l\'interface d\'administration.')
        return redirect('home')

    client_profile, _ = Client.objects.get_or_create(user=request.user)

    if request.method == 'POST' and 'submit_avis' in request.POST:
        commande = get_object_or_404(Commande, pk=request.POST.get('commande_id'), client=client_profile, statut='CONFIRMEE')
        avis_form = AvisForm(request.POST)
        if Avis.objects.filter(commande=commande).exists():
            messages.warning(request, 'Vous avez déjà donné votre avis sur cette prestation.')
        elif avis_form.is_valid():
            avis = avis_form.save(commit=False)
            avis.commande = commande
            avis.client = client_profile
            avis.artisan = commande.artisan
            avis.save()
            messages.success(request, 'Merci, votre avis est publié sur le profil de l\'artisan.')
        else:
            messages.error(request, 'Votre avis n\'a pas pu être enregistré. Vérifiez la note choisie.')
        return redirect('client_dashboard')

    demandes = (
        DemandeService.objects.filter(client=client_profile)
        .select_related('metier')
        .annotate(devis_count=Count('devis'))
        .order_by('-created_at')
    )
    commandes = _attach_steps(list(
        Commande.objects.filter(client=client_profile)
        .select_related('artisan__user', 'artisan__metier', 'devis__demande')
        .order_by('-created_at')
    ))
    avis_by_commande = {a.commande_id: a for a in Avis.objects.filter(commande__in=[c.id for c in commandes])}
    for c in commandes:
        c.mon_avis = avis_by_commande.get(c.id)

    return render(request, 'dashboard/client.html', {
        'client_profile': client_profile,
        'demandes': demandes,
        'commandes': commandes,
        'avis_form': AvisForm(),
        'counts': {
            'demandes_ouvertes': sum(1 for d in demandes if d.statut == 'EN_ATTENTE'),
            'devis_recus': Devis.objects.filter(demande__client=client_profile, statut='EN_ATTENTE').count(),
            'commandes_actives': sum(1 for c in commandes if c.statut in ('EN_ATTENTE', 'EN_COURS', 'TERMINEE')),
            'a_valider': sum(1 for c in commandes if c.statut == 'TERMINEE'),
        },
    })


# ---------------------------------------------------------------------------
# Espace artisan
# ---------------------------------------------------------------------------

@login_required
def artisan_dashboard_view(request):
    if request.user.role == 'CLIENT':
        return redirect('client_dashboard')
    if request.user.role != 'ARTISAN':
        messages.info(request, 'Les administrateurs gèrent la plateforme depuis l\'interface d\'administration.')
        return redirect('home')

    artisan_profile, created = Artisan.objects.get_or_create(user=request.user, defaults={'ville': 'Bamako'})
    if created or not artisan_profile.metier_id:
        messages.info(request, 'Complétez votre profil (métier, zone, tarif) pour recevoir les demandes de votre secteur.')

    realisation_form = RealisationForm()
    profile_form = ArtisanProfileUpdateForm(instance=artisan_profile)
    active_tab = request.GET.get('onglet', 'demandes')

    if request.method == 'POST':
        if 'add_realisation' in request.POST:
            realisation_form = RealisationForm(request.POST, request.FILES)
            active_tab = 'portfolio'
            if realisation_form.is_valid():
                realisation = realisation_form.save(commit=False)
                realisation.artisan = artisan_profile
                realisation.save()
                messages.success(request, 'Réalisation ajoutée à votre portfolio.')
                return redirect('/dashboard/artisan/?onglet=portfolio')
        elif 'update_profile' in request.POST:
            profile_form = ArtisanProfileUpdateForm(request.POST, request.FILES, instance=artisan_profile)
            active_tab = 'profil'
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profil professionnel mis à jour.')
                return redirect('/dashboard/artisan/?onglet=profil')

    devis_envoyes = Devis.objects.filter(artisan=artisan_profile).values_list('demande_id', flat=True)
    matching_demandes = (
        DemandeService.objects.filter(metier=artisan_profile.metier, statut='EN_ATTENTE')
        .exclude(pk__in=devis_envoyes)
        .select_related('client__user', 'metier')
        .annotate(devis_count=Count('devis'))
        .order_by('-created_at')[:12]
        if artisan_profile.metier_id else DemandeService.objects.none()
    )
    mes_devis = Devis.objects.filter(artisan=artisan_profile).select_related('demande__client__user', 'demande__metier').order_by('-created_at')
    commandes = _attach_steps(list(
        Commande.objects.filter(artisan=artisan_profile)
        .select_related('client__user', 'devis__demande')
        .order_by('-created_at')
    ))
    avis_recus = artisan_profile.avis_recus.select_related('client__user').order_by('-created_at')
    stats = avis_recus.aggregate(avg=Avg('note'), count=Count('id'))

    return render(request, 'dashboard/artisan.html', {
        'artisan': artisan_profile,
        'matching_demandes': matching_demandes,
        'mes_devis': mes_devis,
        'commandes': commandes,
        'realisations': artisan_profile.realisations.all(),
        'avis_recus': avis_recus,
        'avg_rating': stats['avg'],
        'avis_count': stats['count'],
        'realisation_form': realisation_form,
        'profile_form': profile_form,
        'active_tab': active_tab,
        'chiffre_confirme': sum(c.devis.montant for c in commandes if c.statut == 'CONFIRMEE'),
    })


@login_required
@require_POST
def commande_action_view(request, pk, action):
    """Transitions de statut d'une commande, alignees sur les regles de l'API REST."""
    commande = get_object_or_404(Commande.objects.select_related('client__user', 'artisan__user'), pk=pk)
    user = request.user
    is_artisan = commande.artisan.user_id == user.id
    is_client = commande.client.user_id == user.id
    fallback = 'artisan_dashboard' if is_artisan else 'client_dashboard'

    if action == 'demarrer' and is_artisan:
        if commande.statut != 'EN_ATTENTE':
            messages.warning(request, 'Cette commande ne peut pas être démarrée dans son état actuel.')
        else:
            commande.statut = 'EN_COURS'
            commande.date_debut = timezone.now()
            commande.save(update_fields=['statut', 'date_debut', 'updated_at'])
            messages.success(request, 'Intervention démarrée. Le client voit l\'avancement dans son espace.')
    elif action == 'terminer' and is_artisan:
        if commande.statut != 'EN_COURS':
            messages.warning(request, 'Seule une commande en cours peut être déclarée terminée.')
        else:
            commande.statut = 'TERMINEE'
            commande.date_fin_reelle = timezone.now()
            commande.save(update_fields=['statut', 'date_fin_reelle', 'updated_at'])
            messages.success(request, 'Travaux déclarés terminés. En attente de validation par le client.')
    elif action == 'confirmer' and is_client:
        if commande.statut != 'TERMINEE':
            messages.warning(request, 'La prestation doit être déclarée terminée par l\'artisan avant validation.')
        else:
            commande.statut = 'CONFIRMEE'
            commande.save(update_fields=['statut', 'updated_at'])
            messages.success(request, 'Prestation validée. Vous pouvez maintenant noter l\'artisan.')
    elif action == 'annuler' and (is_client or is_artisan):
        if commande.statut in ('TERMINEE', 'CONFIRMEE', 'ANNULEE'):
            messages.warning(request, 'Cette commande ne peut plus être annulée.')
        else:
            commande.statut = 'ANNULEE'
            commande.save(update_fields=['statut', 'updated_at'])
            messages.info(request, 'Commande annulée.')
    else:
        messages.error(request, 'Action non autorisée sur cette commande.')

    return _redirect_back(request, fallback)


@login_required
@require_POST
def realisation_delete_view(request, pk):
    realisation = get_object_or_404(Realisation.objects.select_related('artisan__user'), pk=pk)
    if realisation.artisan.user_id != request.user.id:
        messages.error(request, 'Vous ne pouvez supprimer que vos propres réalisations.')
    else:
        realisation.delete()
        messages.success(request, 'Réalisation supprimée.')
    return redirect('/dashboard/artisan/?onglet=portfolio')


# ---------------------------------------------------------------------------
# Authentification (session web)
# ---------------------------------------------------------------------------

def _dashboard_for(user):
    return {'ARTISAN': 'artisan_dashboard', 'CLIENT': 'client_dashboard'}.get(user.role, 'home')


def login_view(request):
    if request.user.is_authenticated:
        return redirect(_dashboard_for(request.user))

    next_url = request.POST.get('next') or request.GET.get('next', '')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.cleaned_data['user']
        login(request, user)
        messages.success(request, f'Bon retour parmi nous, {user.first_name or user.email}.')
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
            return redirect(next_url)
        return redirect(_dashboard_for(user))

    return render(request, 'auth/login.html', {'form': form, 'next': next_url})


def register_view(request):
    if request.user.is_authenticated:
        return redirect(_dashboard_for(request.user))

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
                    Client.objects.create(user=user, ville=data['ville'], quartier=data['quartier'], adresse=data['adresse'])
                else:
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
                    )
            login(request, user)
            messages.success(request, f'Bienvenue sur ArtisanConnect, {user.first_name}. Votre compte est prêt.')
            return redirect(_dashboard_for(user))
    else:
        role = request.GET.get('role', 'CLIENT')
        form = RegisterForm(initial={'role': role if role in ('CLIENT', 'ARTISAN') else 'CLIENT', 'ville': 'Bamako'})

    return render(request, 'auth/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Vous êtes déconnecté. À bientôt sur ArtisanConnect.')
    return redirect('home')
