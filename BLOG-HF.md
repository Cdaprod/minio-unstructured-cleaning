 Title: Streamline ETL Operations with Python: Transferring Data from MinIO to Weaviate Utilizing Unstructured

Introduction
------------

MinIO, a popular High Performance Object Storage system, often serves as a reliable data lake for many enterprises and institutions. As a flexible and scalable solution, MinIO provides efficient means for storing large volumes of structured and unstructured data. However, deriving valuable insights from raw data requires additional processing and refinement before applying machine learning algorithms. To bridge this gap, we introduce a simple yet powerful solution leveraging Python scripts, Unstructured.io, and Weaviate vector databases for seamlessly transferring and transforming data assets stored in MinIO.

This write-up highlights a proof of concept (PoC) illustrating how to harness the power of Python, MinIO, Unstructured.io, and Weaviate vector databases to create an effective ETL pipeline. Users can execute the accompanying Python scripts to achieve the following objectives:

1. Set up connections to a running instance of Weaviate.
2. Design a schema for storing documents within Weaviate utilizing the UnstructuredDocument class.
3. Develop utility functions for manipulating files stored in MinIO object storage and processing them to derive meaningful information.
4. Demonstrate the execution flow starting from downloading files from a designated MinIO bucket, followed by processing PDFs to extract textual content, and concluding with uploading the derived data to Weaviate.
5. Query the Weaviate vector database post-execution to examine the imported records.

MinIO - Preparations
-------------------

Before proceeding, ensure proper setup and configuration of MinIO server and data sets for experimentation purposes. Herein, we demonstrate connecting to a remote MinIO deployment hosted under *[play.min.io](http://play.min.io)* domain and employing the publicly available **cda-datasets** bucket pre-populated with sample PDF files. Optionally, interested readers might consider setting up a private MinIO environment and populate it accordingly.

Python Dependencies
------------------

Begin by fulfilling the necessary dependencies outlined in the PoC description. Installing packages such as `weaviate-client`, `unstructured`, and `minio` ensures compatibility across different modules involved in constructing the proposed ETL pipeline. Fire off the subsequent command in terminal windows or similar environments to satisfy the requirements:

```bash
pip install weaviate-client unstructured minio
```

Weaviate Setup
-------------

Kickstart the Weaviate vector database either manually or programmatically prior to initiating any ETL activities. If unfamiliar with launching Weaviate, consult official [documentation](<https://www.semitechnologies.com/developers/weaviate/>\*)*\* for detailed guidance. Throughout the PoC, assume a local Weaviate instance operates successfully on port number *8080*, serving as the intended recipient for data exported from MinIO.

ETL Pipeline Construction
------------------------

After installing the necessary dependencies, our journey through constructing an effective ETL pipeline begins, marrying the robust capabilities of MinIO, Unstructured.io, and Weaviate with Python's versatility. This section will navigate through the intricacies of schema creation, utility function development, and the orchestration of these components to realize a seamless data flow from extraction to queryable insights within Weaviate.

### Weaviate Schema Creation

Our initial step towards integrating with the Weaviate vector database involves defining a schema tailored to our data needs. The schema acts as a blueprint, informing Weaviate about the type of data we plan to store and query. For this POC, we focus on a schema class named `NewUnstructuredDocument`, designed to encapsulate the essence of our documents with properties like 'title', 'content', 'datePublished', and 'url'.

```python
import weaviate

client = weaviate.Client("http://localhost:8080")

schema = {
    "classes": [
        {
            "class": "NewUnstructuredDocument",
            "properties": [
                {"name": "title", "dataType": ["string"], "description": "Document title"},
                {"name": "content", "dataType": ["text"], "description": "Document content"},
                {"name": "datePublished", "dataType": ["date"], "description": "Publication date"},
                {"name": "url", "dataType": ["string"], "description": "Document URL"}
            ],
            "description": "Stores documents with structured metadata"
        }
    ]
}

client.schema.delete_class('UnstructuredDocument')
client.schema.create(schema)
```

This schema creation step is crucial, as it directly impacts how data is ingested, indexed, and queried within Weaviate. It signifies the preparation of our vector database to receive and understand the structured data derived from our raw, unstructured sources.

### Utility Functions for ETL Operations

#### MinIO Interaction

Interfacing with MinIO involves initializing a client with access credentials and creating a function dedicated to downloading files from a specified bucket. This function is pivotal in the 'Extract' phase of our ETL pipeline, ensuring that our source documents are locally available for processing.

```python
from minio import Minio
import os

minio_client = Minio("play.min.io:443", access_key="minioadmin", secret_key="minioadmin", secure=True)

def download_files_from_minio(bucket_name, local_dir="downloaded_data"):
    objects = minio_client.list_objects(bucket_name, recursive=True)
    for obj in objects:
        file_path = os.path.join(local_dir, obj.object_name)
        minio_client.fget_object(bucket_name, obj.object_name, file_path)
    print(f"Downloaded files to {local_dir}")
```

#### Processing Documents with Unstructured.io

The processing of PDFs to extract text employs Unstructured.io, a library adept at handling various unstructured data formats. By partitioning PDFs into elements, we can extract textual content effectively, preparing it for ingestion into Weaviate.

```python
from pathlib import Path
from unstructured.partition.pdf import partition_pdf

def process_pdfs_and_extract_text(local_dir="downloaded_data"):
    text_elements = []
    for pdf_path in Path(local_dir).glob("*.pdf"):
        text_elements.extend(partition_pdf(str(pdf_path)))
    return text_elements
```

#### Data Ingestion into Weaviate

The final step involves uploading the processed data to Weaviate, mapping the extracted text to the previously defined schema properties. This function encapsulates the 'Load' phase, transforming our data into a queryable state within the vector database.

```python
def upload_data_to_weaviate(elements):
    for element in elements:
        data_object = {
            "title": element.metadata.get("title"),
            "content": element.text,
            "datePublished": element.metadata.get("datePublished"),
            "url": element.metadata.get("url")
        }
        client.data_object.create(data_object, class_name="NewUnstructuredDocument")
    print("Data uploaded to Weaviate")
```

### Execution and Querying

Combining these components into a cohesive script enables the execution of the entire ETL process in a streamlined manner. Upon successful data ingestion, querying Weaviate for the imported records allows us to verify the outcome and explore the ingested data.

```python
if __name__ == "__main__":
    download_files_from_minio("cda-datasets")
    elements = process_pdfs_and_extract_text()
    upload_data_to_weaviate(elements)

# Query Weaviate for verification
query_result = client.query.get("NewUnstructuredDocument", ["title", "content"]).do()
```

This POC not only demonstrates the feasibility of extracting valuable insights from unstructured data but also showcases the seamless integration of distinct technologies to achieve a robust ETL pipeline. By adhering to best practices and leveraging the strengths of MinIO, Unstructured.io, and Weaviate, we unlock a pathway to enhanced data understanding and utilization, pivotal for data-driven decision-making in today's digital era.