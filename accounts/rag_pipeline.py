import os
import pandas as pd
from dotenv import load_dotenv

# LangChain community integrations
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.tools import DuckDuckGoSearchRun

# Groq LLM
from langchain_groq import ChatGroq

# LangChain core
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

# ✅ New imports for LangChain 1.0.2
# from langchain.chains.retrieval_qa.base import RetrievalQA
# from langchain.chains.combine_documents.base import create_stuff_documents_chain

# Load environment variables
load_dotenv()


# ======================
# 🔹 Step 1: Data ingestion from transactions.csv
# ======================
def init_vector_db():
    df_path = os.path.join("finance", "data", "transactions.csv")
    if not os.path.exists(df_path):
        raise FileNotFoundError(f"Transaction file not found: {df_path}")

    df = pd.read_csv(df_path)

    # Convert each row into a readable text chunk
    texts = [
        f"Date: {r['Date']}, Category: {r['Category']}, Amount: ₹{r['Amount']}, Description: {r.get('Description', '')}"
        for _, r in df.iterrows()
    ]

    embedding = OllamaEmbeddings(model="nomic-embed-text")
    persist_directory = "chroma_db"

    # Load or create the vector DB
    if os.path.exists(persist_directory) and os.listdir(persist_directory):
        db = Chroma(persist_directory=persist_directory, embedding_function=embedding)
    else:
        db = Chroma.from_texts(texts, embedding, persist_directory=persist_directory)
        db.persist()

    return db


# ======================
# 🔹 Step 2: Initialize Groq LLM
# ======================
def init_llm():
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("⚠️ GROQ_API_KEY not found in .env file")

    llm = ChatGroq(
        api_key=groq_api_key,
        model="mixtral-8x7b",
        temperature=0.6
    )
    return llm


# ======================
# 🔹 Step 3: Prompt template
# ======================
prompt = ChatPromptTemplate.from_template("""
You are a proactive financial and trip-planning assistant.
You understand user spending patterns from their transactions and can plan trips within given budgets.
Always provide concise, realistic, and actionable financial insights.

If the user asks about:
- Spending → analyze from transactions and summarize.
- Savings → suggest monthly saving plans.
- Trip → use DuckDuckGo search results to recommend cost-effective options.

<context>
{context}
</context>

User Query: {input}

Think step by step and provide a helpful, data-informed response.
""")


# ======================
# 🔹 Step 4: Create RAG chain manually
# ======================
def create_rag_chain():
    db = init_vector_db()
    retriever = db.as_retriever()
    llm = init_llm()

    # Create a basic document processing chain
    document_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)

    # ✅ For LangChain v1.0.2, use RetrievalQA instead of create_retrieval_chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt}
    )

    return qa_chain


# ======================
# 🔹 Step 5: Handle user query (with optional web data)
# ======================
def handle_query(user_query):
    search = DuckDuckGoSearchRun()
    retrieval_chain = create_rag_chain()

    # Add extra info if it's a travel-related question
    if any(word in user_query.lower() for word in ["trip", "travel", "hotel", "vacation"]):
        web_data = search.run(user_query)
        user_query += f"\n\nExtra travel info from web:\n{web_data}"

    response = retrieval_chain.invoke({"query": user_query})
    return response.get("result", "Sorry, I couldn’t find a clear answer.")
