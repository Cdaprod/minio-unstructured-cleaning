# Streamlining Data ETL from MinIO to Weaviate: A Python-Powered Approach

In the ever-evolving landscape of data management and analysis, organizations constantly seek efficient ways to process and leverage their vast data reserves. This article presents a comprehensive Proof of Concept (POC) that showcases how to streamline the Extract, Transform, and Load (ETL) process of unstructured data from MinIO to Weaviate using Python, focusing on PDF documents as our primary data source.

## Introduction

Our POC leverages three powerful tools:
- **MinIO**: An object storage solution that's highly compatible with Amazon S3, ideal for storing unstructured data like PDFs.
- **Unstructured.io**: A Python library designed to parse and extract text from various unstructured document formats.
- **Weaviate**: An open-source vector database perfect for enabling semantic search and AI-driven data analysis.

By integrating these technologies, we aim to create a pipeline that not only simplifies data ingestion from PDF documents but also enriches the data analysis capabilities of businesses and researchers alike.

## Setting Up the Environment

Before diving into the code, ensure you have a running instance of MinIO and Weaviate. Both can be set up locally or hosted on cloud services. For MinIO, we'll use the publicly accessible endpoint `play.min.io` for demonstration purposes, and Weaviate will be running locally.

### Installing Necessary Packages

The Python ecosystem offers a range of libraries that simplify working with data. For this POC, you'll need to install the following packages:

```bash
pip install weaviate-client unstructured minio
```

## Building the ETL Pipeline

### Step 1: Connecting to MinIO

First, initialize the MinIO client. Replace `endpoint`, `access_key`, and `secret_key` with your MinIO instance details.

```python
from minio import Minio

# Initialize the MinIO client
minioClient = Minio(
    "play.min.io:443",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=True
)
```

### Step 2: Downloading PDF Files from MinIO

Create a function to download PDF files from a specified bucket. This example uses a bucket named `cda-datasets`.

```python
import os

def download_files_from_minio(bucket_name, local_dir="downloaded_data"):
    objects = minioClient.list_objects(bucket_name, recursive=True)
    os.makedirs(local_dir, exist_ok=True)
    for obj in objects:
        if obj.object_name.endswith('.pdf'):
            file_path = os.path.join(local_dir, obj.object_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            minioClient.fget_object(bucket_name, obj.object_name, file_path)
            print(f"Downloaded {obj.object_name} to {file_path}")
```

### Step 3: Extracting Text from PDFs Using Unstructured.io

After downloading the PDFs, we'll extract their textual content using `unstructured`.

```python
from unstructured.partition.pdf import partition_pdf
from pathlib import Path

def process_pdfs_and_extract_text(local_dir="downloaded_data"):
    elements_list = []
    for pdf_file in Path(local_dir).glob("*.pdf"):
        elements = partition_pdf(filename=str(pdf_file))
        for element in elements:
            elements_list.append(element.text)
    return elements_list
```

### Step 4: Creating a Weaviate Schema and Ingesting Data

Now, define a schema in Weaviate for the extracted text and upload the data.

```python
import weaviate

client = weaviate.Client("http://localhost:8080")

# Define the schema
schema = {
    "classes": [
        {
            "class": "Document",
            "description": "A class to store extracted document texts",
            "properties": [
                {"name": "text", "dataType": ["text"], "description": "The text of the document"}
            ]
        }
    ]
}

# Create the schema in Weaviate
client.schema.create(schema)

def upload_data_to_weaviate(texts):
    for text in texts:
        data_object = {"text": text}
        client.data_object.create(data_object, class_name="Document")
        print("Uploaded text to Weaviate")
```

### Step 5: Querying Weaviate

After uploading the data, you can perform semantic searches within Weaviate to find relevant documents based on the content.

```python
query_result = client.query.get("Document", properties=["text"]).with_limit(10).do()
for item in query_result['data']['Get']['Document']:
    print(item['text'])
```

## Conclusion and Further Steps

This POC demonstrates a straightforward approach to automating the ETL process from MinIO to Weaviate, focusing on extracting textual content from PDF documents. This pipeline not only simplifies data ingestion but also opens up opportunities for advanced semantic analysis and AI-driven insights.

### Expanding the POC

- **Real-time Processing**: Implement event-driven data ingestion using MinIO's notification system.
- **Handling More Document Types**: Extend the pipeline to include other formats like DOCX, HTML, and images with OCR capabilities.
- **Advanced Analytics**: Leverage Weaviate's vector search for clustering, similarity search, and building recommendation systems.

By building on this foundation, organizations can harness the full potential of their unstructured data, driving innovation and informed decision-making.

---

This article provides a comprehensive guide with code snippets to implement the POC, offering insights into each step of the process and suggestions for further enhancements.