from supabase import create_client, Client
from settings import SUPABASE_URL, SUPABASE_KEY

# Initialize Supabase client
supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def download_image_db(storage_bucket: str, download_path: str) -> bytes | None:
    """Download an image from Supabase storage and return raw bytes."""
    try:
        print("Running download_image_db")
        response = supabase_client.storage.from_(storage_bucket).download(download_path)

        if response is None:
            raise ValueError("Failed to download image.")

        return response  # This is already in `bytes` format

    except Exception as error:
        print(f"Error downloading image: {str(error)}")
        return None