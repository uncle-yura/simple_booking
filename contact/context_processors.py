from .models import ContactsList, SocialContact

def contact_short(request):
    contacts = ContactsList.objects.filter(content_short__isnull=False)[:4]
    return { 'contact_short' : contacts,
    }

def contact_social(request):
    contact_social = SocialContact.objects.all()
    return { 'contact_social' : contact_social,
    }
