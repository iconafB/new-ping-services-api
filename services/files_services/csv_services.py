from fastapi import UploadFile,HTTPException,status
import polars as pl
from io import BytesIO
import re
from utils.logging.logger import define_logger

csv_logger=define_logger("csv_logger","logs/csv_route.log")

class CSVClass:

    #csv data extraction
    async def data_extraction(self,file:UploadFile):

        if not file.filename or not file.filename.lower().endswith(".csv"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Only csv files are allowed")
        try:
            content=await file.read()
            df=pl.read_csv(content)
            cleaned_cell_numbers:list[str]=self.exctract_clean_sa_cell_numbers(df)
            return cleaned_cell_numbers
        
        except Exception as e:
            csv_logger.exception(f"an exception occurred while extracting data from a csv file:{str(e)}")
            raise 
    
    async def data_bulk_insertion(self,data:list[str])->list[str]:
        try:
            return
        except Exception as e:
            csv_logger.exception(f"exception occurred while inserting csv data into a pings table:{str(e)}")
            raise
    
    async def csv_file_cleaner(self,data:UploadFile):
        try:
            return True
        
        except Exception as e:
            csv_logger.exception(f"an internal server error occurred while cleaning the csv file:{str(e)}")
            raise 

    def normalize_csv_numbers(self,row:str)->str | None:
        if row is None:
            return None
        digits=re.sub(r"\D", "", str(row).strip())

        if not digits:
            return None
        #missing leading zero
        if len(digits)==9 and digits.startswith(("6","7","8")):
            digits="0" + digits
        if len(digits)==10 and digits.startswith(("06","07","08")):
            return digits
        
        if len(digits)==11 and digits.startswith(("276","277",278)):
            return "0"+ digits[:2]
        return None
    
    #This method extract cell numbers and duplicates

    def exctract_clean_sa_cell_numbers(self,df:pl.DataFrame,column_name:str |None=None)->list[str]:

        target_column=column_name or df.columns[0]
        if target_column not in df.columns:
            raise ValueError(f"Column '{target_column}' not found")
        raw_numbers = df[target_column].cast(pl.Utf8, strict=False).to_list()
        cleaned_numbers:list[str]=[]
        seen:set[str]=set()
        for row in raw_numbers:
            normalized_cell_number=self.normalize_csv_numbers(row)
            if normalized_cell_number is not None and normalized_cell_number not in seen:
                seen.add(normalized_cell_number)
                cleaned_numbers.append(normalized_cell_number)
        
        return cleaned_numbers
    

