import boto3
import sqlite3
from unstructured.partition.pdf import partition_pdf
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.graphs import Neo4jGraph
import os

class DocumentProcessor:
    def __init__(self):
        self.s3 = boto3.client('s3',
                               endpoint_url=os.getenv('WASABI_ENDPOINT'),
                               aws_access_key_id=os.getenv('WASABI_ACCESS_KEY'),
                               aws_secret_access_key=os.getenv('WASABI_SECRET_KEY'))
        self.bucket = os.getenv('WASABI_BUCKET')
        self.conn = sqlite3.connect('documents.db')
        self.create_table()
        self.embeddings = OpenAIEmbeddings()
        self.neo4j_graph = Neo4jGraph(
            url=os.getenv('NEO4J_URI'),
            username=os.getenv('NEO4J_USERNAME'),
            password=os.getenv('NEO4J_PASSWORD')
        )

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents
        (id INTEGER PRIMARY KEY, filename TEXT, s3_path TEXT, user TEXT)
        ''')
        self.conn.commit()

    def process_document(self, file, user):
        # Upload to Wasabi
        filename = file.name
        s3_path = f"documents/{user}/{filename}"
        self.s3.upload_fileobj(file, self.bucket, s3_path)

        # Save metadata to SQLite
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO documents (filename, s3_path, user) VALUES (?, ?, ?)",
                       (filename, s3_path, user))
        self.conn.commit()

        # Process with unstructured
        elements = partition_pdf(file)
        text = "\n\n".join([str(el) for el in elements])

        # Split text
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_text(text)

        # Store in Chroma
        Chroma.from_texts(splits, self.embeddings, metadatas=[{"source": s3_path}] * len(splits))

        # Store in Neo4j (simplified, you might want to add more complex graph structures)
        self.neo4j_graph.query(
            "CREATE (d:Document {path: $path, user: $user})",
            {"path": s3_path, "user": user}
        )