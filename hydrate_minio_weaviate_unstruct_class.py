from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import requests
from io import BytesIO
from minio import Minio
import weaviate
import os
import tempfile
import re
from unstructured.partition.auto import partition
from langchain_core.runnables import RunnableLambda

app = FastAPI()

# Setup for MinIO and Weaviate
minio_client = Minio("192.168.0.25:9000", access_key="cda_cdaprod", secret_key="cda_cdaprod", secure=False)
weaviate_client = weaviate.Client("http://192.168.0.25:8080")
bucket_name = "cda-datasets"

class URLList(BaseModel):
    urls: List[str]

# Assuming minio_client and other necessary clients (like for Weaviate) are initialized globally or passed during class initialization

class DETLIngestionPipeline:
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        
        # Initialize RunnableLambdas if needed
        self.upload_file_runnable = RunnableLambda(self.upload_text_to_minio)
        self.load_file_from_minio = RunnableLambda(self.load_file)  # Define this method if needed
        self.list_bucket_objects = RunnableLambda(self.list_objects)  # Define this method if needed

    @tool
    def sanitize_url_to_object_name(self, url: str) -> str:
        clean_url = re.sub(r'^https?://', '', url)
        clean_url = re.sub(r'[^\w\-_\.]', '_', clean_url)
        return clean_url[:250] + '.txt'

    @tool
    def prepare_text_for_tokenization(self, text: str) -> str:
        clean_text = re.sub(r'\s+', ' ', text).strip()
        return clean_text

    @tool
    def extract_text_from_html(self, html_content: bytes) -> str:
        elements = partition(file=BytesIO(html_content), content_type="text/html")
        combined_text = "\n".join([e.text for e in elements if hasattr(e, 'text')])
        return self.prepare_text_for_tokenization(combined_text)

    @tool
    def upload_text_to_minio(self, object_name: str, text: str):
        with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8", suffix=".txt") as tmp_file:
            tmp_file.write(text)
            tmp_file_path = tmp_file.name

        minio_client.fput_object(self.bucket_name, object_name, tmp_file_path)
        os.remove(tmp_file_path)  # Clean up after uploading

    @tool
    def process_url(self, url: str):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Check for HTTP issues

            combined_text = self.extract_text_from_html(response.content)
            object_name = self.sanitize_url_to_object_name(url)

            self.upload_text_to_minio(object_name, combined_text)

            # Insert into Weaviate or other operations can be added here

        except requests.RequestException as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch URL {url}: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing {url}: {e}")

    def run(self, url_list: List[str]):
        for url in url_list:
            self.process_url(url)

    async def arun(self, url_list: List[str]):
        import asyncio

        tasks = [asyncio.create_task(self.process_url(url)) for url in url_list]
        await asyncio.gather(*tasks)

# Usage example:
detl_pipeline = DETLIngestionPipeline(bucket_name=bucket_name)
detl_pipeline.run(url_list=['http://example.com'])
await detl_pipeline.arun(url_list=['http://example.com'])