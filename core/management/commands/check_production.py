from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Check production readiness with security validation'

    def add_arguments(self, parser):
        parser.add_argument('--prod-check', action='store_true',
                            help='Simulate production environment check')

    def handle(self, *args, **options):
        if options['prod_check']:
            self.stdout.write(
                self.style.WARNING('Simulating production environment check...')
            )
            
            # Save current environment variables
            original_debug = os.environ.get('DEBUG')
            original_ssl = os.environ.get('SECURE_SSL_REDIRECT')
            original_hsts = os.environ.get('SECURE_HSTS_SECONDS')
            original_session = os.environ.get('SESSION_COOKIE_SECURE')
            original_csrf = os.environ.get('CSRF_COOKIE_SECURE')
            
            try:
                # Set production-like environment
                os.environ['DEBUG'] = 'False'
                os.environ['SECURE_SSL_REDIRECT'] = 'True'
                os.environ['SECURE_HSTS_SECONDS'] = '31536000'
                os.environ['SESSION_COOKIE_SECURE'] = 'True'
                os.environ['CSRF_COOKIE_SECURE'] = 'True'
                
                self.stdout.write('Running deployment check with production settings...')
                call_command('check', '--deploy')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error during production check: {e}')
                )
            finally:
                # Restore original environment
                if original_debug is not None:
                    os.environ['DEBUG'] = original_debug
                else:
                    os.environ.pop('DEBUG', None)
                    
                if original_ssl is not None:
                    os.environ['SECURE_SSL_REDIRECT'] = original_ssl
                else:
                    os.environ.pop('SECURE_SSL_REDIRECT', None)
                    
                if original_hsts is not None:
                    os.environ['SECURE_HSTS_SECONDS'] = original_hsts
                else:
                    os.environ.pop('SECURE_HSTS_SECONDS', None)
                    
                if original_session is not None:
                    os.environ['SESSION_COOKIE_SECURE'] = original_session
                else:
                    os.environ.pop('SESSION_COOKIE_SECURE', None)
                    
                if original_csrf is not None:
                    os.environ['CSRF_COOKIE_SECURE'] = original_csrf
                else:
                    os.environ.pop('CSRF_COOKIE_SECURE', None)
        else:
            self.stdout.write('Current Django configuration check:')
            call_command('check', '--deploy')
            
            self.stdout.write('\n' + '='*50)
            self.stdout.write('DEPLOYMENT READINESS SUMMARY:')
            self.stdout.write('='*50)
            
            # Check key settings
            debug_status = '❌ CRITICAL' if settings.DEBUG else '✅ OK'
            secret_key_status = '❌ WEAK' if (
                len(settings.SECRET_KEY) < 50 or 
                'django-insecure' in settings.SECRET_KEY
            ) else '✅ STRONG'
            
            self.stdout.write(f'DEBUG Setting: {debug_status}')
            self.stdout.write(f'SECRET_KEY: {secret_key_status}')
            
            if settings.DEBUG:
                self.stdout.write(
                    self.style.WARNING(
                        '\n⚠️  Currently in DEVELOPMENT mode'
                    )
                )
                self.stdout.write(
                    'To test production readiness:'
                )
                self.stdout.write(
                    '1. Set DEBUG=False in .env file'
                )
                self.stdout.write(
                    '2. Set security settings to True'
                )
                self.stdout.write(
                    '3. Re-run: python manage.py check --deploy'
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        '\n✅ Production configuration active'
                    )
                )