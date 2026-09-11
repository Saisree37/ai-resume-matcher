from app.models.job import Job
from app.schemas.job import JobCreate
from app.database import session
from fastapi import Depends,APIRouter
from sqlalchemy.orm import Session
from fastapi import HTTPException
from fastapi import UploadFile, File
import pymupdf
from app.services.resume_processor import (
    clean_resume_text,
    create_resume_document,
    calculate_match_score,
    extract_job_skills,
    extract_resume_strengths,
    parse_skill_match_response,
    create_resume_retriever,
    create_rag_context,
    prompt_template,
    create_rag_chain,
    vector_store,
    
)

from langchain_text_splitters import RecursiveCharacterTextSplitter

router = APIRouter()


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()



@router.post("/jobs")
def Jobcreate(jobcreate:JobCreate,db:Session = Depends(get_db)):
    new_job = Job(**jobcreate.model_dump())

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job

@router.get("/jobs")
def get_jobs(db:Session = Depends(get_db)):
    get_db = db.query(Job).all()
    return get_db

@router.get("/jobs/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):

    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.delete("/jobs/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):

    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    db.delete(job)
    db.commit()
    return "product deleted"

@router.post("/jobs/{job_id}/match")
async def match_job(
    job_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # Get job from database
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    # Validate PDF
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF resume"
        )

    try:

        # Read PDF
        pdf_bytes = await file.read()

        # Extract text
        with pymupdf.open(
            stream=pdf_bytes,
            filetype="pdf"
        ) as doc:

            resume_text = ""

            for page in doc:
                resume_text += page.get_text("text") + "\n"

        # Clean resume text
        cleaned_text = clean_resume_text(resume_text)

        # Calculate semantic match score
        score = calculate_match_score(
            cleaned_text,
            job.description
        )

        # --------------------------------
        # 7.2.1 Extract required JD skills
        # --------------------------------

        required_skills = extract_job_skills(
            job.description
        )

        # --------------------------------
        # Create resume document
        # --------------------------------

        document = create_resume_document(
            cleaned_text
        )

        # Split document into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

        chunks = text_splitter.split_documents(
            [document]
        )

        # --------------------------------
        # RAG
        # --------------------------------

        store = vector_store(chunks)

        retriever = create_resume_retriever(
            store
        )

        # --------------------------------
        # 7.1 / 7.2 Matching
        # --------------------------------

        prompt, resume_context = prompt_template(
            retriever,
            job.description,
            required_skills
        )

        rag_chain = create_rag_chain(
            prompt
        )

        response = rag_chain.invoke({
            "required_skills": required_skills,
            "resume_context": create_rag_context(
                resume_context
            )
        })

        # --------------------------------
        # Convert LLM response into lists
        # --------------------------------

        skill_result = parse_skill_match_response(
            response.content
        )

        matched_skills = skill_result[
            "matched_skills"
        ]

        missing_skills = skill_result[
            "missing_skills"
        ]

        # --------------------------------
        # 7.3 Strengths
        # --------------------------------

        strengths = extract_resume_strengths(
    matched_skills,
    create_rag_context(resume_context)
)

        # --------------------------------
        # Final response
        # --------------------------------

        return {
            "job_id": job.id,
            "job_title": job.title,
            "company": job.company,
            "match_score": round(score, 2),

            "analysis": {
                "required_skills": required_skills,
                "matched_skills": matched_skills,
                "skill_gaps": missing_skills,
                "strengths": strengths,
                "improvement_suggestions": missing_skills
            }
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )