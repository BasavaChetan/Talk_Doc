import streamlit as st
from azure.storage.blob import BlobClient
from dotenv import load_dotenv
import os

load_dotenv()
ACCOUNT_NAME = os.environ.get("AZURE_ACCOUNT_NAME")
ACCOUNT_KEY = os.environ.get("AZURE_ACCOUNT_KEY")
CONTAINER_NAME = os.environ.get("CONTAINER_NAME")
AZURE_CONNECTION_STRING = os.environ.get("AZURE_CONNECTION_STRING")

def upload_to_blob(uploaded_file):
    try:
        # Azure blob details
        connection_string = AZURE_CONNECTION_STRING 
        container_name = CONTAINER_NAME 
        blob_name = uploaded_file.name

        blob_client = BlobClient.from_connection_string(connection_string, container_name, blob_name)
        
        # Define chunk size (4MB in this example)
        chunk_size = 4 * 1024 * 1024
        block_ids = []
        block_id_prefix = "block-"

        while True:
            chunk = uploaded_file.read(chunk_size)
            if not chunk:
                break

            block_id = block_id_prefix + format(len(block_ids), '05d')
            blob_client.stage_block(block_id, chunk)
            block_ids.append(block_id)

        blob_client.commit_block_list(block_ids)
        return True
    except Exception as e:
        st.error(f"Error uploading to blob: {e}")
        return False


