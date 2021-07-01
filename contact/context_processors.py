from .models import ContactsList

def contact_short(request):
    contacts = ContactsList.objects.filter(content_short__isnull=False)[:4]
    return { 'contact_short' : contacts,
    }