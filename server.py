from fastapi import FastAPI, Query, UploadFile
from typing import Annotated
from rag_worker import rag
from dotenv import load_dotenv
load_dotenv()
from rq_client import queue
from email_agent import email_worker
app = FastAPI()
@app.get('/')
def read_root():
    return {"message": "Hello, FastAPI!"}
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    try:
        file_path = f"uploads/{file.filename}"
        file_path = f"uploads/{file.filename}"

        with open(file_path, "wb") as f:
            f.write(await file.read())

        job = queue.enqueue(rag, file_path)
        return {"message": "File saved successfully", "path": f"/uploads/{file.filename}","job":job.id}
        
    except Exception as e:
        return {"message": e.args}
@app.get("/job-status")
def getUploadResult( job_id: str = Query(...,description="Job ID")
):
    
    job = queue.fetch_job(job_id=job_id)
    resut = job.result
    return{"result": resut}

@app.post("/chat")
def chat(query:str = Query(...,description="User Query")):
    job = queue.enqueue(email_worker, query)
    return {"job":job.id}

@app.get("/chat-job-status")
def getChatResult(job_id: str = Query(...)):
    job = queue.fetch_job(job_id)

    if job is None:
        return {"status": "not_found"}

    if job.is_failed:
        return {"status": "failed", "error": str(job.exc_info)}

    if job.result is None:
        return {"status": "processing"}

    return {"status": "finished", "result": job.result}
