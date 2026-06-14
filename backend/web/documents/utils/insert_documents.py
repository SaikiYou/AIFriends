from pathlib import Path

import lancedb

from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import LanceDB
from langchain_text_splitters import RecursiveCharacterTextSplitter

from web.documents.utils.custom_embeddings import CustomEmbeddings


def insert_documents():
    # Resolve data.txt relative to this module file:
    data_file = Path(__file__).resolve().parent.parent / "data.txt"
    if not data_file.exists():
        raise FileNotFoundError(f"data.txt not found at {data_file}")
    loader = TextLoader(str(data_file), encoding="utf-8")

    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)
    print(f'已切分成 {len(texts)} 个文本片段')

    embeddings = CustomEmbeddings()
    db = lancedb.connect(str(Path(__file__).resolve().parent.parent / 'lancedb_storage'))
    vector_db = LanceDB.from_documents(
        documents=texts,
        embedding=embeddings,
        connection=db,
        table_name='my_knowledge_base',
        mode='overwrite'
    )
    print(f'已插入{vector_db._table.count_rows()}条数据')