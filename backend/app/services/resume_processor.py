import re
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
import numpy as np
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

def clean_resume_text(text: str):
    lines = text.splitlines()

    cleaned_lines = []

    for line in lines:
        line = line.strip()
        line = " ".join(line.split())

        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)

def extract_sections(text: str):
    identify_sections = ["summary",
    "about me",
    "experience summary",
    "skills",
    "technical skills",
    "professional summary",
    "experience",
    "work experience",
    "education",
    "certifications",
    "projects",
    "achievements"]
    return_sections = {}
    current_section = None
    for line in text.splitlines():
        line = line.lower().strip()
        line = line.rstrip(":")
        if line in identify_sections:
            current_section = line
            return_sections[current_section] = []
        elif current_section and line:
            return_sections[current_section].append(line)
    return return_sections

def extract_skills(section):

    if "skills" in section:
        skill_section = section["skills"]

    elif "technical skills" in section:
        skill_section = section["technical skills"]

    else:
        return []

    cleaned_skills = []

    for skill_text in skill_section:

        skills = re.split(r"[,|]", skill_text)

        for skill in skills:
            skill = skill.strip()

            if skill and skill not in cleaned_skills:
                cleaned_skills.append(skill)

    return cleaned_skills


def create_resume_document(text):
    return Document(
        page_content=text,
        metadata={"source": "resume"}
    )

def embedding_model():
    embeddings = OllamaEmbeddings(
        model=os.getenv("OLLAMA_EMBEDDING_MODEL"),
        base_url=os.getenv("OLLAMA_BASE_URL")
    )
    return embeddings

def vector_store(chunks):

    embeddings = embedding_model()

    vector_store = Chroma(
        collection_name="resume_collection",
        embedding_function=embeddings,
        
    )

    vector_store.add_documents(chunks)

    return vector_store

def search_resume(vector_store, query):
    results = vector_store.similarity_search(query, k=3)
    return results

def cosine_similarity(v1, v2):
    """Calculate the cosine similarity between two vectors."""
    # Convert lists to numpy arrays
    a = np.array(v1)
    b = np.array(v2)
    
    # Formula: (A · B) / (||A|| * ||B||)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def calculate_match_score(resume_text, job_description):
    embeddings = embedding_model()
    resume_embedding = embeddings.embed_query(resume_text)
    job_embedding = embeddings.embed_query(job_description)
    score = cosine_similarity(resume_embedding,job_embedding)
    return (score + 1) / 2 * 100

def match_resume_with_job(resume_text, job_description):
    score = calculate_match_score(resume_text, job_description)

    return {
        "match_score": round(score, 2)
    }

def create_resume_retriever(vector_store):
    retriever = vector_store.as_retriever(
        search_kwargs={"k": 3}
    )
    return retriever

#retriever.invoke() returns Document objects
def retrieve_resume_context(retriever, job_description):
    retriever_resume = retriever.invoke(job_description)
    return retriever_resume


def create_rag_context(documents):
    # Extract page_content from each document and join them with a newline
    combined_text = "\n\n".join(doc.page_content for doc in documents)
    return combined_text




def create_llm():
    llm = ChatOllama(
        model=os.getenv("OLLAMA_LLM_MODEL"),
        temperature=0,
        base_url=os.getenv("OLLAMA_BASE_URL")
    )
    return llm



def create_rag_chain(prompt):
    llm = create_llm()
    chain = prompt | llm
    return chain

def extract_job_skills(job_description):

    llm = create_llm()

    prompt = ChatPromptTemplate.from_template("""
    You are a job description skill extraction assistant.

    Your task is to extract the skills and technical requirements
    explicitly mentioned in the job description.

    Job Description:
    {job_description}

    Instructions:
    - Extract only skills and technical requirements explicitly
      mentioned in the job description.
    - Do not infer skills that are not mentioned.
    - Do not use outside knowledge.
    - Do not include responsibilities, job titles, company names,
      certifications, or soft skills.
    - Avoid duplicate skills.
    - Return only the skill names.
    - Do not provide explanations.

    Return the result in this format:

    Required Skills:
    - skill 1
    - skill 2
    - skill 3

    If no skills are found, return:

    Required Skills:
    - None
    """)

    chain = prompt | llm

    response = chain.invoke({
        "job_description": job_description
    })

    return response.content


def prompt_template(retriever, job_description, required_skills):

    resume_context = retrieve_resume_context(
        retriever,
        job_description
    )

    prompt = ChatPromptTemplate.from_template("""
    You are a resume matching assistant.

    Your task is to compare the required skills from the job description
    with the candidate's resume context retrieved using RAG.

    Required Skills from Job Description:
    {required_skills}

    Relevant Resume Context:
    {resume_context}

    Instructions:
    - Compare every required skill against the relevant resume context.
    - Mark a skill as matched only when there is clear evidence in the resume.
    - Do not assume or infer skills that are not supported by the resume.
    - Do not use outside knowledge.
    - Do not add skills that are not present in the required skills list.
    - If a required skill is not supported by the resume context, add it
      to the Missing Skills list.
    - Do not treat unrelated resume skills as matched skills.
    - Consider equivalent wording when the resume clearly describes the
      same skill or technology.
    - Every item in Matched Skills must come from the Required Skills list.
    - Every item in Missing Skills must come from the Required Skills list.
    - A skill cannot appear in both Matched Skills and Missing Skills.
    - Return only the matched and missing skills.
    - Do not provide explanations or additional analysis.

    Output format:

    Matched Skills:
    - skill 1
    - skill 2

    Missing Skills:
    - skill 1
    - skill 2

    If there are no matched skills:
    Matched Skills:
    - None

    If there are no missing skills:
    Missing Skills:
    - None
    """)

    return prompt, resume_context

def parse_strengths_response(response):

    strengths = []

    lines = response.splitlines()

    current_section = False

    for line in lines:

        line = line.strip()

        if line == "Strengths:":
            current_section = True
            continue

        if current_section and line.startswith("-"):

            strength = line[1:].strip()

            if strength and strength.lower() != "none":
                strengths.append(strength)

    return strengths


def parse_skill_match_response(response):

    matched_skills = []
    missing_skills = []

    lines = response.splitlines()

    current_section = None

    for line in lines:

        line = line.strip()

        if line == "Matched Skills:":
            current_section = "matched"
            continue

        if line == "Missing Skills:":
            current_section = "missing"
            continue

        if line.startswith("-") and current_section:

            skill = line[1:].strip()

            if skill and skill.lower() != "none":

                if current_section == "matched":
                    matched_skills.append(skill)

                elif current_section == "missing":
                    missing_skills.append(skill)

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }


def extract_resume_strengths(matched_skills, retriever_resume):

    llm = create_llm()

    prompt = ChatPromptTemplate.from_template("""
    You are an expert resume analysis assistant.

    Your task is to identify the candidate's strongest qualifications
    based only on the matched skills and the relevant resume context.

    Matched Skills:
    {matched_skills}

    Resume Context:
    {retriever_resume}

    Instructions:

    - Identify strengths only from the matched skills.
    - Every strength must be directly related to a matched skill.
    - Use ONLY actual resume content as evidence.
    - Every strength must have clear supporting evidence in the resume context.
    - Do not include missing or unmatched skills.
    - Do not include unrelated technical skills from the resume.
    - Ignore vector database metadata, document metadata, object
      representations, memory addresses, tags, class names, library
      internals, and system-generated information.
    - Do not treat the presence of a technology inside a Python object,
      metadata field, tag, or RAG implementation as evidence of experience.
    - Do not infer or assume experience.
    - Do not use outside knowledge.
    - Do not include soft skills, personality traits, job titles,
      company names, or certifications.
    - Do not invent experience or proficiency levels.
    - Do not simply repeat the skill name. Describe the relevant
      experience or qualification when the resume provides evidence.
    - Return only the strengths.

    Output format:

    Strengths:
    - strength 1
    - strength 2
    - strength 3

    If no relevant strengths are supported by the resume:

    Strengths:
    - None
    """)

    chain = prompt | llm

    response = chain.invoke({
        "matched_skills": matched_skills,
        "retriever_resume": retriever_resume
    })

    return parse_strengths_response(response.content)