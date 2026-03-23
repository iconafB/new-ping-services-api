from fastapi import UploadFile
from utils.logging.logger import define_logger
csv_logger=define_logger("csv_logger","logs/csv_route.log")

class CSVClass:
    #csv data extraction
    async def data_extraction(self,data:UploadFile):
        try:
            return False
        except Exception as e:
            csv_logger.exception(f"an exception occurred while extracting data from a csv file:{str(e)}")
            raise 
    
    #csv data deduplication
    async def deduplication(self,data:list[str])->list[str]:
        try:
            return False
        except Exception as e:
            csv_logger.exception(f"an exception occurred while running data deduplication:{str(e)}")
            raise 
    
    async def data_bulk_insertion(self,data:list[str]):
        try:
            return
        except Exception as e:
            csv_logger.exception(f"exception occurred while inserting csv data into a pings table:{str(e)}")
            raise

