# serviceapp/storages.py
from storages.backends.azure_storage import AzureStorage
from django.conf import settings

class AzureMediaStorage(AzureStorage):
    account_name = settings.AZURE_ACCOUNT_NAME  # Azure Storage Account Name
    account_key = settings.AZURE_ACCOUNT_KEY    # Azure Storage Account Key
    container_name = settings.AZURE_CONTAINER_NAME   # Azure Storage Container Name
    expiration_secs = settings.AZURE_CONNECTION_STRING  # Optional: set expiry for signed URLs
