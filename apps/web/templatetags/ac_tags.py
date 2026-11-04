"""Filtres de presentation partages par les templates ArtisanConnect."""
from decimal import Decimal, InvalidOperation

from django import template
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()

# Correspondance metier -> visuel genere (static/images/generated/).
# Sert de repli lorsque le metier n'a pas d'image televersee dans MEDIA.
METIER_VISUALS = {
    'menuiserie': 'hero_atelier',
    'plomberie': 'metier_plomberie',
    'electricite': 'metier_electricite',
    'électricité': 'metier_electricite',
    'couture': 'metier_couture',
    'soudure': 'metier_soudure',
    'maconnerie': 'metier_maconnerie',
    'maçonnerie': 'metier_maconnerie',
    'peinture': 'metier_peinture',
    'climatisation': 'metier_climatisation',
    'mecanique': 'metier_mecanique',
    'mécanique': 'metier_mecanique',
    'coiffure': 'metier_coiffure',
    'coiffure & esthétique': 'metier_coiffure',
    'coiffure & esthetique': 'metier_coiffure',
}

STATUS_TONES = {
    'EN_ATTENTE': 'pending',
    'EN_COURS': 'progress',
    'ACCEPTEE': 'success',
    'ACCEPTE': 'success',
    'CONFIRMEE': 'success',
    'TERMINEE': 'done',
    'REFUSE': 'danger',
    'ANNULEE': 'danger',
    'ANNULE': 'danger',
    'EXPIRE': 'muted',
}


@register.filter
def fcfa(value):
    """Formate un montant en FCFA avec separateur de milliers (ex: 25 000 FCFA)."""
    try:
        amount = Decimal(value or 0)
    except (InvalidOperation, TypeError, ValueError):
        return value
    formatted = f'{amount:,.0f}'.replace(',', '\u202f')
    return f'{formatted}\u00a0FCFA'


@register.simple_tag
def metier_image(metier):
    """Retourne l'URL d'illustration d'un metier (media televerse ou visuel genere)."""
    if metier is None:
        return static('images/generated/hero_atelier.jpg')
    image = getattr(metier, 'image', None)
    if image:
        try:
            return image.url
        except ValueError:
            pass
    key = (getattr(metier, 'nom', '') or '').strip().lower()
    visual = METIER_VISUALS.get(key, 'hero_atelier')
    return static(f'images/generated/{visual}.jpg')


@register.filter
def status_tone(statut):
    return STATUS_TONES.get(statut, 'muted')


@register.simple_tag
def stars(note, size='sm'):
    """Affiche une note sur 5 avec des icones etoiles (pleines, demi, vides)."""
    try:
        value = float(note or 0)
    except (TypeError, ValueError):
        value = 0.0
    parts = []
    for i in range(1, 6):
        if value >= i:
            icon = 'bi-star-fill'
        elif value >= i - 0.5:
            icon = 'bi-star-half'
        else:
            icon = 'bi-star'
        parts.append(f'<i class="bi {icon}" aria-hidden="true"></i>')
    label = f'Note : {value:.1f} sur 5'.replace('.', ',')
    return format_html(
        '<span class="ac-stars ac-stars--{}" role="img" aria-label="{}">{}</span>',
        size, label, mark_safe(''.join(parts)),
    )


@register.filter
def initials(user):
    first = (getattr(user, 'first_name', '') or '')[:1]
    last = (getattr(user, 'last_name', '') or '')[:1]
    return (first + last).upper() or (getattr(user, 'email', '?')[:1].upper())


@register.filter
def rating_display(value):
    """Note moyenne lisible ; renvoie None si aucun avis (affiche 'Nouveau')."""
    if value in (None, ''):
        return None
    try:
        return f'{float(value):.1f}'.replace('.', ',')
    except (TypeError, ValueError):
        return None


@register.simple_tag
def artisan_avatar(artisan):
    """Retourne l'URL de photo de l'artisan ou un portrait genere realiste."""
    if artisan is None:
        return None
    photo = getattr(artisan, 'photo_profil', None)
    if photo:
        try:
            return photo.url
        except ValueError:
            pass

    user = getattr(artisan, 'user', None)
    first_name = (getattr(user, 'first_name', '') or '').strip().lower()
    name_map = {
        'mamadou': 'portrait_mamadou.jpg',
        'seydou': 'portrait_seydou.jpg',
        'oumar': 'portrait_oumar.jpg',
        'aminata': 'portrait_aminata.jpg',
        'bakary': 'portrait_bakary.jpg',
    }
    if first_name in name_map:
        return static(f'images/generated/{name_map[first_name]}')

    metier_nom = ''
    if getattr(artisan, 'metier', None):
        metier_nom = (getattr(artisan.metier, 'nom', '') or '').strip().lower()

    metier_avatar_map = {
        'maconnerie': 'metier_maconnerie.jpg',
        'maçonnerie': 'metier_maconnerie.jpg',
        'peinture': 'metier_peinture.jpg',
        'climatisation': 'metier_climatisation.jpg',
        'mecanique': 'metier_mecanique.jpg',
        'mécanique': 'metier_mecanique.jpg',
        'coiffure': 'metier_coiffure.jpg',
        'coiffure & esthétique': 'metier_coiffure',
        'coiffure & esthetique': 'metier_coiffure',
        'menuiserie': 'portrait_seydou.jpg',
        'plomberie': 'portrait_mamadou.jpg',
        'electricite': 'portrait_oumar.jpg',
        'électricité': 'portrait_oumar.jpg',
        'couture': 'portrait_aminata.jpg',
        'soudure': 'portrait_bakary.jpg',
    }
    if metier_nom in metier_avatar_map:
        return static(f'images/generated/{metier_avatar_map[metier_nom]}')

    return None

