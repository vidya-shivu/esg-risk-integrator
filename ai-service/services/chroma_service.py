import chromadb
from data.esg_docs import documents

# ✅ Create local ChromaDB client
client = chromadb.Client()

# ✅ Create collection
collection = client.get_or_create_collection(
    name="esg_knowledge"
)

# ✅ Seed only once
existing = collection.count()

if existing == 0:

    for i, doc in enumerate(documents):

        collection.add(
            documents=[doc],
            ids=[str(i)]
        )

    print("✅ ChromaDB seeded with ESG documents")

else:
    print("✅ ChromaDB already contains documents")


# ✅ Search function
def search_esg_knowledge(query):

    results = collection.query(
        query_texts=[query],
        n_results=2
    )

    return results['documents'][0]