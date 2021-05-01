from .base import *

# Core
SECURE_SSL_REDIRECT = True
ALLOWED_HOSTS = [
    '.smilewestada.com',
    '.herokuapp.com',
]

# SendGrid
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
SENDGRID_API_KEY = env("SENDGRID_API_KEY")
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
SENDGRID_TRACK_CLICKS_HTML = False
SENDGRID_TRACK_CLICKS_PLAIN = False

# Sentry
SENTY_RELEASE = env("HEROKU_SLUG_COMMIT")

# Cloudinary
CLOUDINARY_STORAGE = {
    'PREFIX': 'smilewestada',
}
