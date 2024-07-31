from pydantic import BaseModel, validator
import requests
from minio import Minio
import weaviate
import os
import tempfile
import re
from unstructured.partition.auto import partition
import io

# Pydantic models for data cleaning and validation
class URLSanitizerModel(BaseModel):
    url: str

    @validator('url', pre=True, allow_reuse=True)
    def sanitize(cls, v: str) -> str:
        clean_url = re.sub(r'^https?://', '', v)
        clean_url = re.sub(r'[^\w\-_\.]', '_', clean_url)
        return clean_url[:250] + '.txt'

class TextPreparatorModel(BaseModel):
    text: str

    @validator('text', pre=True, allow_reuse=True)
    def prepare(cls, v: str) -> str:
        clean_text = re.sub(r'\s+', ' ', v).strip()
        return clean_text

# Setup for MinIO and Weaviate
minio_client = Minio("192.168.0.25:9000", access_key="cda_cdaprod", secret_key="cda_cdaprod", secure=False)
print("MinIO client initialized.")

client = weaviate.Client("http://192.168.0.25:8080")
print("Weaviate client initialized.")

bucket_name = "cda-datasets"

# Encapsulated functions for processing
def sanitize_url_to_object_name(url: str) -> str:
    return URLSanitizerModel(url=url).url

def prepare_text_for_tokenization(text: str) -> str:
    return TextPreparatorModel(text=text).text

def process_and_store_url(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP issues

        html_content = io.BytesIO(response.content)
        elements = partition(file=html_content, content_type="text/html")
        combined_text = "\n".join([e.text for e in elements if hasattr(e, 'text')])
        combined_text = prepare_text_for_tokenization(combined_text)
        object_name = sanitize_url_to_object_name(url)

        with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8", suffix=".txt") as tmp_file:
            tmp_file.write(combined_text)
            tmp_file_path = tmp_file.name
        
        minio_client.fput_object(bucket_name, object_name, tmp_file_path)
        print(f"Stored '{object_name}' in MinIO bucket '{bucket_name}'.")
        os.remove(tmp_file_path)  # Clean up
    except requests.RequestException as e:
        print(f"Failed to fetch URL {url}: {e}")
    except Exception as e:
        print(f"Error processing {url}: {e}")

def process_and_insert_document(object_name: str):
    try:
        file_path = object_name
        minio_client.fget_object(bucket_name, object_name, file_path)
        
        elements = partition(filename=file_path)
        text_content = "\n".join([e.text for e in elements if hasattr(e, 'text')])
        
        data_object = {"source": object_name, "content": text_content}
        client.data_object.create(data_object, "Document")
        print(f"Inserted document '{obj.object_name}' into Weaviate.")
        
        os.remove(file_path)  # Clean up
    except Exception as e:
        print(f"Error processing document '{object_name}': {e}")

# Main processing logic
if not minio_client.bucket_exists(bucket_name):
    minio_client.make_bucket(bucket_name)
    print(f"Bucket '{bucket_name}' created.")

urls = [ ... ]  # Your URLs list goes here

for url in urls:
    process_and_store_url(url)

for obj in minio_client.list_objects(bucket_name, recursive=True):
    if obj.object_name.endswith('.txt'):
        print(f"Processing document: {obj.object_name}")
        process_and_insert_document(obj.object_name)
