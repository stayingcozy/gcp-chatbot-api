from supabase import create_client, Client
from settings import SUPABASE_URL, SUPABASE_KEY

# Google Cloud #

def access_secret_version(secret_id, version_id="latest"):
    """ Return the value of a google cloud secret's latest version """
    from google.cloud import secretmanager

    # Create the secret manager client
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version
    name = f"{secret_id}/versions/{version_id}"

    # Access the secret version
    print(f"Attempting to access secret: {name}")
    response = client.access_secret_version(name=name)

    # Return the decoded payload
    return response.payload.data.decode("UTF-8")

# Supabase #

def create_supabase_client():
    """ Initialize Supabase client ~~secretly~~ """
    url = access_secret_version(SUPABASE_URL) 
    key = access_secret_version(SUPABASE_KEY) 

    return create_client(url, key)

supabase_client: Client = create_supabase_client()


def download_image_db(storage_bucket: str, download_path: str) -> bytes | None:
    """Download an image from Supabase storage and return raw bytes."""
    try:
        response = supabase_client.storage.from_(storage_bucket).download(download_path)

        if response is None:
            raise ValueError("Failed to download image.")

        return response  # This is already in `bytes` format

    except Exception as error:
        print(f"Error downloading image: {str(error)}")
        return None
    