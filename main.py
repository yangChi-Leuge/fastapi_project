from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import uuid
import deepl


app = FastAPI(
    title="Image Upload and Translation API",
    description="API to upload, delete images, and translate text.",
    version="1.0.0",
)

# 이미지 파일 저장 디렉토리
UPLOAD_DIRECTORY = "./uploaded_images"

# 디렉토리가 없으면 생성
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

class TranslationRequest(BaseModel):
    language: str
    text: str

# 이미지 업로드 엔드포인트
@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    """
    Upload an image.

    - **file**: Upload a JPEG or PNG image file.
    """
    # 파일 저장 경로 설정
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIRECTORY, file_id + os.path.splitext(file.filename)[1])

    # 파일 저장
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # 파일 ID 반환
    return {"file_id": file_id}

# 이미지 삭제 엔드포인트
@app.delete("/delete-image/{file_id}")
async def delete_image(file_id: str):
    """
    Delete an image by file_id.

    - **file_id**: The unique ID of the image to delete.
    """
    # 디렉토리 내 파일 검색 및 삭제
    for filename in os.listdir(UPLOAD_DIRECTORY):
        if filename.startswith(file_id):
            file_path = os.path.join(UPLOAD_DIRECTORY, filename)
            os.remove(file_path)
            return JSONResponse(content={"message": "File deleted successfully"})

    raise HTTPException(status_code=404, detail="File not found")

# Deepl 인증 키
auth_key = "7ee2dece-f6ed-4a1c-9734-4e71c5912854"
translator = deepl.Translator(auth_key)

class TranslationRequest(BaseModel):
    language: str  # en, ko, de, fr, zh, ja, it, pl
    text: str

@app.post("/translate/")
async def translate_text(request: TranslationRequest):
    """
    Translate text to the specified language using Deepl.

    - **request**: TranslationRequest containing language code and text to translate.
    """
    # 입력된 언어 코드가 유효한지 확인
    supported_languages = ["en", "kr", "germ", "fran", "chi", "jp", "ital", "pli"]
    if request.language not in supported_languages:
        raise HTTPException(status_code=400, detail="Unsupported language code")

    try:
        # Deepl을 사용한 번역
        type = "EN-US"

        if (request.language == "kr"):
            type = "KO"
        elif (request.language == "germ"):
            type = "DE"
        elif (request.language == "fran"):
            type = "FR"
        elif (request.language == "chi"):
            type = "ZH"
        elif (request.language == "jp"):
            type = "JA"
        elif (request.language == "ital"):
            type = "IT"
        elif (request.language == "pli"):
            type = "PL"

        translated_text = translator.translate_text(request.text, target_lang=type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")

    return {"translated_text": translated_text.text}



#
# translator = Translator()
# class TranslationRequest(BaseModel):
#     language: str  # en, kr, germ, fran, chi, jp, ital, pli
#     text: str
#
# @app.post("/translate/")
# async def translate_text(request: TranslationRequest):
#     """
#     Detect language and translate text to the specified language.
#
#     - **request**: TranslationRequest containing language code and text to translate.
#     """
#     # 입력된 언어 코드가 유효한지 확인
#     supported_languages = ["en", "kr", "germ", "fran", "chi", "jp", "ital", "pli"]
#     if request.language not in supported_languages:
#         raise HTTPException(status_code=400, detail="Unsupported language code")
#
#     try:
#         # 언어 감지
#         detected_lang = translator.detect(request.text).lang
#
#         type = "en"
#
#         if (request.language == "kr"):
#             type = "ko"
#         elif (request.language == "germ"):
#             type = "de"
#         elif (request.language == "fran"):
#             type = "fr"
#         elif (request.language == "chi"):
#             type = "zh"
#         elif (request.language == "jp"):
#             type = "ja"
#         elif (request.language == "ital"):
#             type = "it"
#         elif (request.language == "pli"):
#             type = "pl"
#         translated_text = translator.translate(request.text, src=detected_lang, dest=type).text
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")
#
#     return {"detected_language": LANGUAGES.get(detected_lang).title(), "translated_text": translated_text}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
