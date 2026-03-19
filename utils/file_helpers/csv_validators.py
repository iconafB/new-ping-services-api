from fastapi import UploadFile, HTTPException, status
from utils.constants import ALLOWED_CSV_CONTENT_TYPES
import csv
from utils.logging.logger import define_logger
csv_validator_logger=define_logger("csv_validator_logger","logs/csv_files_route.log")

async def validate_csv_files(file: UploadFile) -> UploadFile:

    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="No file uploaded")

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Only files with .csv extension are allowed")

    if file.content_type not in ALLOWED_CSV_CONTENT_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Invalid content type '{file.content_type}'. Only CSV files are allowed")
    
    try:
        chunk=await file.read(4096)
        if not chunk:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Uploaded file is empty")
        chunk.decode("utf-8")
    except UnicodeEncodeError as u:
        csv_validator_logger.exception(f"an encoding error occurred while validating the csv file:{u}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"CSV file must be UTF-8 encoded")
    
    except HTTPException:
        raise
    
    except Exception as e:
        csv_validator_logger.exception(f"an internal server error occurred while validating a csv file:{e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while validating a csv file")
    finally:
        await file.seek(0)
    
    return file


