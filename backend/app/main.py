from fastapi import FastAPI,UploadFile,File,HTTPException
import logging
import pymupdf
from app.routers.jobs import router as jobs_router
from app.database import Base, engine
from app.services.resume_processor import  create_resume_retriever,retrieve_resume_context,create_rag_context,prompt_template,create_rag_chain,retrieve_resume_context,create_rag_chain,prompt_template,create_resume_retriever,match_resume_with_job,create_resume_document,clean_resume_text,extract_sections,extract_skills,vector_store,search_resume,calculate_match_score
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.services.resume_processor import embedding_model
from langchain_chroma import Chroma
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(jobs_router)

Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return "ai-resume-matcher"

@app.post("/Upload_file")
async def upload_file(file: UploadFile = File(...)):
    # 1. Validate that the uploaded file is a PDF
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Please upload a valid PDF document."
        )
    
    try:
        # 2. Read the file contents into memory bytes
        pdf_bytes = await file.read()
        
        # 3. Open the PDF from the memory stream
        # Specifying filetype="pdf" ensures PyMuPDF parses the stream correctly
        with pymupdf.open(stream=pdf_bytes, filetype="pdf") as doc:
            extracted_text = []
            
            # 4. Iterate through each page and extract text
            for page_num, page in enumerate(doc):
                page_text = page.get_text("text")  # "text" mode is optimal for standard layouts
                extracted_text.append({
                    "page": page_num + 1,
                    "text": page_text.strip()
                })
            resume_text = "\n".join(page["text"] for page in extracted_text)

            cleaned_text = clean_resume_text(resume_text)
            extract_section = extract_sections(cleaned_text)
            extract_skill = extract_skills(extract_section)
            document = create_resume_document(cleaned_text)
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50
            )
            chunks = text_splitter.split_documents([document])
            store = vector_store(chunks)
            retriever = create_resume_retriever(store)

            results = retriever.invoke(
                "Python backend development experience"
            )

            

            results = search_resume(
                store,
                "Python backend development experience"
            )

            
            result = match_resume_with_job(
                cleaned_text,
                """
                Looking for a Python Backend Developer with experience in
                Django, PostgreSQL, REST APIs, Docker and Git.
                """
            )

                        
            job_description = """
            Looking for a Python Backend Developer with experience
            in FastAPI, PostgreSQL and Docker.
            """

            resume_context = retrieve_resume_context(
                retriever,
                job_description
            )

            prompt = prompt_template(
                retriever,
                job_description
            )

            chain = create_rag_chain(prompt)

            response = chain.invoke({
                "job_description": job_description,
                "resume_context": create_rag_context(resume_context)
            })

        # 5. Return structured JSON payload
        return {
            "filename": file.filename,
            "total_pages": len(extracted_text),
            "content": cleaned_text,
            "sections": extract_section,
            "skills": extract_skill
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
