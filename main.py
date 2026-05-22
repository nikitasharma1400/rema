from dotenv import load_dotenv

load_dotenv()
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from extractor import extract_pdf_text, extract_url_text, extract_youtube_text
from chunker import chunk_text
from embeddings import embed_chunks
from rag import generate_report

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "REMA backend is alive"}


@app.post("/process")
async def process_source(
    source_type: str = Form(...),
    url: str = Form(None),
    file: UploadFile = File(None),
):
    try:
        if source_type == "pdf":
            if file is None:
                raise HTTPException(status_code=400, detail="PDF file is required.")
            text = await extract_pdf_text(file)

        elif source_type == "url":
            if not url:
                raise HTTPException(status_code=400, detail="URL is required.")
            text = extract_url_text(url)

        elif source_type == "youtube":
            if not url:
                raise HTTPException(status_code=400, detail="YouTube URL is required.")
            text = extract_youtube_text(url)

        else:
            raise HTTPException(status_code=400, detail="Invalid source type.")

        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted.")

        chunks = chunk_text(text)

        if not chunks:
            raise HTTPException(status_code=400, detail="No chunks were created.")

        #embedded_chunks = embed_chunks(chunks)

        report = generate_report(chunks)

        return {
            "source_type": source_type,
            "total_chunks": len(chunks),
            "report": report,
            "sources": [
                {
                    "id": index + 1,
                    "text": chunk[:500],
                }
                for index, chunk in enumerate(chunks[:8])
            ],
        }

    except HTTPException:
        raise

    except Exception as error:
        print("PROCESS ERROR:", error)
        raise HTTPException(status_code=500, detail=str(error))