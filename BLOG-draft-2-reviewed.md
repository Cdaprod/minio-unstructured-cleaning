# Streamlining ETL Processes from MinIO to Weaviate Using Python

Unstructured data, especially in the form of PDF documents, poses significant challenges in data analytics. This Proof of Concept (POC) aims to address these challenges by demonstrating a streamlined method for extracting, transforming, and loading data from MinIO into Weaviate using Python. The goal is to make unstructured data not only accessible but also searchable and analyzable in a vector database environment.

## Introduction to the Concept

The process begins with the extraction of text from PDF files stored in MinIO. This extracted text is then transformed into a structured format suitable for ingestion by Weaviate. Transforming unstructured data into a queryable and meaningful form is crucial for leveraging the full potential of a vector database.

### Addressing the Challenges

Achieving data quality and consistency is crucial, given the diverse formats of documents. It's essential to maintain the integrity and accuracy of information during the extraction phase. As data volumes increase, the system must scale effectively, ensuring optimal performance without compromising on quality. Additionally, ensuring data security and compliance with regulatory standards is fundamental to the system's architecture.

### Opportunities for Innovation

Incorporating AI and machine learning enhances the pipeline's capabilities, enabling deeper insights and predictions. Building knowledge graphs from structured data can unveil complex relationships, providing a richer understanding of the data. Furthermore, adapting the system for real-time data processing can offer instantaneous insights, aligning with the rapid pace of data generation.

## Preparing the Environment

A well-prepared environment is key to the success of technical projects. Access to MinIO and Weaviate instances, along with the installation of essential Python packages, is the first step towards implementing the ETL pipeline.

### Required Python Packages

The Python ecosystem offers libraries that facilitate data manipulation. For this POC, install the necessary packages with:

```bash
pip install weaviate-client unstructured minio
```

## Constructing the ETL Pipeline

### Step 1: Establishing Connection with MinIO

Begin by initializing the MinIO client with your instance details:

```python
from minio import Minio

# Initialize MinIO client
minioClient = Minio(
    "play.min.io:443",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=True
)
```

### Step 2: Retrieving PDF Files from MinIO

Develop a function to download PDFs from a specified bucket, such as `cda-datasets`:

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

### Step 3: Text Extraction from PDFs

Use `unstructured` to extract text from the downloaded PDFs:

```python
from unstructured.partition.pdf import partition_pdf
from pathlib import Path

def process_pdfs_and_extract_text(local_dir="downloaded_data"):
    elements_list = []
    for pdf_file in Path(local_dir).glob("*.pdf"):
        elements = partition_pdf(filename=str(pdf_file))
        elements_list += [element.text for element in elements]
    return elements_list
```

### Step 4: Schema Creation and Data Ingestion in Weaviate

Define a schema in Weaviate for the extracted text and proceed to data upload:

```python
import weaviate

client = weaviate.Client("http://localhost:8080")

# Schema definition
schema = {
    "classes": [
        {
            "class": "Document",
            "description": "Stores extracted document texts",
            "properties": [
                {"name": "text", "dataType": ["text"], "description": "Document text"}
            ]
        }
    ]
}

client.schema.create(schema)

def upload_data_to_weaviate(texts):
    for text in texts:
        client.data_object.create({"text": text}, "Document")
        print("Uploaded text to Weaviate")
```

### Step 5: Semantic Search in Weaviate

Perform semantic searches in Weaviate to locate documents by content:

```python
query_result = client.query.get("Document", properties=["text"]).with_limit(10).do()
for item in query_result['data']['Get']['Document']:
    print(item['text'])
```

## Conclusion and Future Directions

This POC outlines a straightforward method for automating the ETL process from MinIO to Weaviate with a focus on PDF text content. It not only streamlines data ingestion but also lays the groundwork for advanced semantic analysis and AI-driven insights.

### Future Enhancements

- **Real-time Processing**: Implement an event-driven approach using MinIO's notification system.
- **Broadening Document Support**: Expand the pipeline to handle additional formats like DOCX, HTML, and images with OCR.
- **Advanced Analytics**: Utilize Weaviate's vector search capabilities for clustering, similarity searches, and developing recommendation systems.

This foundation enables organizations to exploit their unstructured data fully, fostering innovation and informed decision-making.

---

This guide, complete with code snippets, walks you through each stage of the POC while offering insights into potential enhancements and optimizations.