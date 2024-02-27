import requests
from minio import Minio
import os
from unstructured.partition.auto import partition
import io
import re  # For sanitizing the URL to a valid object name

def sanitize_url_to_object_name(url):
    """
    Sanitize the URL to be used as a valid object name.
    Remove protocol, replace slashes, question marks, and other special characters.
    """
    # Remove http:// or https://
    clean_url = re.sub(r'^https?://', '', url)
    # Replace unwanted characters with an underscore
    clean_url = re.sub(r'[^\w\-_\.]', '_', clean_url)
    # Limit the length of the object name if necessary
    return clean_url[:250] + '.txt'  # Object names can be up to 255 characters for many storage systems

# Initialize MinIO client
minio_client = Minio(
    "cda-DESKTOP:9000",
    access_key="cda_cdaprod",
    secret_key="cda_cdaprod",
    secure=False  # Set to False if not using SSL
)

# Bucket where you want to store the data
bucket_name = "cda-datasets"

# Ensure the bucket exists
if not minio_client.bucket_exists(bucket_name):
    minio_client.make_bucket(bucket_name)

# List of URLs
urls = [
    "https://nanonets.com/blog/langchain/amp/",
    "https://www.sitepoint.com/langchain-python-complete-guide/",
    "https://medium.com/@aisagescribe/langchain-101-a-comprehensive-introduction-guide-7a5db81afa49",
    "https://blog.min.io/minio-langchain-tool",
    "https://quickaitutorial.com/langgraph-create-your-hyper-ai-agent/",
    "https://python.langchain.com/docs/langserve",
    "https://python.langchain.com/docs/expression_language/interface",
    "https://blog.min.io/minio-langchain-tool",
    "https://python.langchain.com/docs/langgraph",
    "https://www.33rdsquare.com/langchain/",
    "https://medium.com/widle-studio/building-ai-solutions-with-langchain-and-node-js-a-comprehensive-guide-widle-studio-4812753aedff", "https://blog.min.io/", "https://sanity.cdaprod.dev/"]

for url in urls:
    response = requests.get(url)
    if response.status_code == 200:
        html_content = io.BytesIO(response.content)  # Wrap the content in a BytesIO object

        # Partition the HTML content specifying the content type
        partitioned_elements = partition(file=html_content, content_type="text/html")

        # Initialize an empty string to hold all text elements
        combined_text = ""

        for element in partitioned_elements:
            if hasattr(element, 'text'):  # If the element has a 'text' attribute
                combined_text += element.text + "\n\n"  # Add a double newline as a separator

        # Sanitize the URL to be used as an object name
        object_name = sanitize_url_to_object_name(url)

        # Save the combined text to a temporary file
        file_path = f"{object_name}"  # Adjust the path as needed
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(combined_text)
        
        # Upload the combined file to MinIO
        minio_client.fput_object(bucket_name, object_name, file_path)
        
        # Optionally remove the file after upload if you're running in a limited storage environment
        os.remove(file_path)