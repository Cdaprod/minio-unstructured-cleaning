To leverage Unstructured exclusively for moving data from S3 to Weaviate, you'd ideally use its modular capabilities for reading, processing, and writing data. Unstructured is designed to work well with text data, particularly for partitioning, processing, and then storing or utilizing this data in various destinations like databases, file systems, or APIs.

However, direct integration between Unstructured and Weaviate through a single line of configuration or a compact code snippet is not natively supported as Unstructured focuses more on the processing of unstructured text data rather than the database interactions. The integration would still require custom code to handle the specifics of reading from S3 (using Unstructured's capabilities or directly through MinIO client) and then writing to Weaviate using its client library.

Here's how you could structure such a process, keeping it as streamlined as possible within the constraints of available libraries:

1. **Read from S3:** Use Unstructured's `S3Reader` or MinIO's client to read files from an S3 bucket.
2. **Process/Partition Text:** Use Unstructured's text processing capabilities to partition or process the text as needed.
3. **Write to Weaviate:** Use the Weaviate Python client to write the processed data to Weaviate.

Since direct code for an "Unstructured exclusive" operation that spans from reading in S3 to writing in Weaviate without explicit steps is not feasible without assuming some processing or handling in between, here's a conceptual approach integrating the steps with a focus on Unstructured processing:

```python
from unstructured.documents.core import S3Document
import weaviate

# Assuming the Unstructured and Weaviate clients are initialized here
weaviate_client = weaviate.Client("your_weaviate_endpoint")

def process_and_store_document(bucket_name, object_name, weaviate_class_name):
    # Create an S3Document for handling S3 data
    document = S3Document.from_s3(bucket_name=bucket_name, key=object_name, s3_client=minio_client)
    
    # Process the document content as needed, e.g., partitioning, extracting text, etc.
    # This step depends on the type of processing you want to perform on your document.
    # For simplicity, assuming the content is directly usable:
    processed_content = document.text  # Simplified; use actual processing as needed
    
    # Create a data object for Weaviate
    data_object = {
        "content": processed_content
    }
    
    # Write the processed content to Weaviate
    weaviate_client.data_object.create(data_object, weaviate_class_name)
    print(f"Uploaded {object_name} to Weaviate in class {weaviate_class_name}")

# Example usage
bucket_name = "your_bucket_name"
object_name = "example.txt"
weaviate_class_name = "WebsiteDataset"

process_and_store_document(bucket_name, object_name, weaviate_class_name)
```

This example abstracts away the specifics of how `S3Document` is implemented with Unstructured and assumes direct use of the MinIO client for S3 interactions. The critical aspect here is the conceptual flow: reading from S3, optionally processing the content, and then writing to Weaviate.

For a truly "Unstructured exclusive" approach, you would focus on leveraging its capabilities for handling and processing text data, while interactions with S3 and Weaviate would still rely on their respective clients or APIs for data transfer operations.