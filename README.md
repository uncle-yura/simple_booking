## Simple Booking
Simple website for providing services 

### Quick start
* Clone this repo
* Create a .env file or use environment variables in another method 
* Install all dependencies `pip install -r requirements.txt`
* Make migrations `python manage.py makemigrations`
* Migrate `python manage.py migrate`
* Create users groups `python manage.py creategroups`
* Collect static files `python manage.py collectstatic`
* (OPTIONAL) Compile ukrainian locale `django-admin compilemessages --locale=uk`
* (OPTIONAL) Compile russian locale `django-admin compilemessages --locale=ru`
* Create super user `python manage.py createsuperuser`
* Create google calendar https://calendar.google.com
* Create google project https://console.cloud.google.com 
* Enable google calendar API
* Create service account and OAuth2 key https://console.cloud.google.com/apis/credentials
* Save service json credentials to 'service_secret.json' in root simple_booking directory
* Add service account to users list in your google calendar
* Create facebook APP https://developers.facebook.com/apps
* Get facebook OAuth2 key https://developers.facebook.com/apps/YOUR_APP/settings/basic/
* (OPTIONAL) Get RECAPTCHA key https://console.cloud.google.com/marketplace/product/google/recaptchaenterprise.googleapis.com
* Run server `python manage.py runserver`
* Create theme and site in Bootstrap_Customizer (Admin panel)
* Configurate django extra settings

### Environment Configuration
The file ".env.example" contains an example of environment variables. 
To use environment variables you can install python-dotenv.
```
from dotenv import load_dotenv

project_home = '/home/user/simple_booking'
load_dotenv(os.path.join(project_home, '.env'))
```

#### Server parameters:
```
export DJANGO_DEBUG="True"
export SERVERNAMES="localhost"
export DJANGO_ADMIN_URL="secureadmin"
export DJANGO_SECRET_KEY="djangosecretkey"
export DJANGO_UNDER_CONSTRUCTION=""
export SERVER_HSTS_SECONDS="3600"
```

#### Database parameters:
```
export SQL_BACKEND="mysql"
export SQL_HOST="sql.host"
export SQL_NAME="sqlname"
export SQL_PORT="3306"
export SQL_PW="sqlpassword"
export SQL_USER="sqluser"
```

#### Social login parameters
```
export DJANGO_AUTH_FACEBOOK_KEY="facebookkey"
export DJANGO_AUTH_FACEBOOK_SECRET="facebooksecret"
export DJANGO_AUTH_GOOGLE_KEY="googlekey"
export DJANGO_AUTH_GOOGLE_SECRET="googlesecret"
```

#### EMail parameters:
```
export DJANGO_EMAIL_HOST="smtp.mail.local"
export DJANGO_EMAIL_HOST_PASSWORD="password"
export DJANGO_EMAIL_HOST_USER="user@mail.local"
export DJANGO_EMAIL_PORT="587"
export DJANGO_EMAIL_USE_SSL=""
export DJANGO_EMAIL_USE_TLS="True"
```

#### Recaptcha parameters:
```
export DJANGO_RECAPTCHA_ACTIVE=""
export DJANGO_RECAPTCHA_PRIVATE_KEY="DJANGO_RECAPTCHA_PRIVATE_KEY"
export DJANGO_RECAPTCHA_PUBLIC_KEY="DJANGO_RECAPTCHA_PUBLIC_KEY"
```

### Configuration django-extra-settings

ABOUT_US (Text) - Text block on index page
FAVICON_LOGO (Image) - Favicon image
FOOTER_BLOCK (Text) - Escape block in footer
FOOTER_COPYRIGHT (String) - Copyright string
FOOTER_DISCLOSURE (Text) - Disclosure text in footer	
FOOTER_FOLLOW (Text) - Escape block after follow block
FOOTER_LOGO	(Image) - Logo image in footer block
HEADER_BLOCK (Text) - Escape block in header
HOW_TO_FIND	(Text) - Escape block in HOW_TO_FIND
NAVBAR_LOGO	(Image) - Logo image in navbar
PRICE_CURRENCY (String) - Currency string (Example: usd)
SITE_COUNTRY (String) - Currency string (Example: USA)
SITE_NAME (String) - Currency string (Example: Booking)
SITE_TITLE (String) - Currency string (Example: Booking site)
