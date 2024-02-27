# Streamlining ETL from MinIO to Weaviate with Python

Navigating the complexities of unstructured data, particularly PDF documents, presents a unique set of challenges in data analytics. This Proof of Concept (POC) is designed to tackle these challenges head-on, demonstrating a streamlined process for extracting, transforming, and loading data from MinIO into Weaviate using Python. The aim is to unlock the potential of unstructured data, making it readily searchable and analyzable.

## Introduction to the Concept

The journey begins with the extraction of text from PDFs stored in MinIO. The extracted text is then transformed into a structured format that Weaviate can ingest. This process is crucial for converting unstructured data into a form that's not just stored but is also meaningful and queryable within a vector database environment. 

### Tackling the Challenges

Ensuring data quality and consistency is paramount. The diversity in document formats means that maintaining the integrity and accuracy of the information during extraction is essential. As the volume of data grows, scalability and performance of the system become critical. The pipeline must efficiently process large datasets, optimizing for speed without sacrificing quality. Moreover, security and compliance are at the forefront of this process. Protecting sensitive information and adhering to stringent data protection regulations are integral to the system's design and operation.

### Opportunities for Expansion

Incorporating AI and machine learning into the pipeline opens up new vistas for data analysis, enabling more nuanced insights and predictions. Similarly, constructing knowledge graphs from the structured data can reveal complex relationships and patterns, offering a deeper understanding of the data landscape. Furthermore, adapting the system for real-time data processing introduces the capability for immediate insights, keeping pace with the velocity of data generation.

## Setting Up the Environment

A conducive environment is the foundation for any successful technical endeavor. Ensuring access to MinIO and Weaviate instances, along with the installation of necessary Python packages, sets the stage for the implementation of the ETL pipeline.

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