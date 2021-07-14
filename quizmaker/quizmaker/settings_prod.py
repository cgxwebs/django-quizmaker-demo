from .settings import env

CSRF_COOKIE_AGE = 7 * 24 * 60 * 60
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755
MEDIA_ROOT = env('MEDIA_ROOT')
STATIC_ROOT = env('STATIC_ROOT')
WSGI_APPLICATION = None
