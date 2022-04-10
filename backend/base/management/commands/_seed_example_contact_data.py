from contact.models import ContactsList, SocialContact


class ExampleContactData:
    def create_social_contact(self):
        for index, value in enumerate(("Instagram", "Facebook", "Twitter")):
            social, created = SocialContact.objects.get_or_create(id=index)
            if created:
                social.share_name = value
                social.share_icon = f"fab fa-{value.lower()}"
                social.share_text = value
                social.share_url = f"http://{value.lower()}.com"
                social.save()

    def create_contacts_list(self):
        for index in range(3):
            contact, created = ContactsList.objects.get_or_create(id=index)
            if created:
                contact.name = f"Example contact #{index}"
                contact.content = (
                    f"<p><b>Name:</b> Example Name {index}</p>"
                    + f"<p><b>Phone:</b> +01234567890{index}</p>"
                    + f"<p><b>Address:</b> Room #{index}</p>"
                )
                contact.content_short = (
                    f"<a href='tel: +01234567890{index}'>+01234567890{index}</a>"
                )
                contact.save()

    def __init__(self, stdout, stderr):
        self.stdout = stdout
        self.stderr = stderr

    def create_data(self):
        self.create_social_contact()
        self.create_contacts_list()
