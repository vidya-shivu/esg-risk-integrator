from services.chroma_service import search_esg_knowledge

results = search_esg_knowledge(
    "Company has weak governance"
)

print(results)