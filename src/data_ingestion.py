import os
import pandas as pd
from google.cloud import storage
from sklearn.model_selection import train_test_split
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml
import sys

logger = get_logger(__name__)

class DataIngestion:
    def __init__(self,config):
        self.config = config["data_ingestion"]
        self.bucket_name = self.config["bucket_name"]
        self.file_name = self.config["bucket_file_name"]
        self.train_test_ratio = self.config["train_ratio"]

        os.makedirs(RAW_DIR, exist_ok=True)
        logger.info(f"Created directory at {RAW_DIR} for raw data storage with {self.bucket_name} and {self.file_name}.")
        
    def download_csv_from_gcp(self):
        try:
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            blob = bucket.blob(self.file_name)
            blob.download_to_filename(RAW_FILE_PATH)
            logger.info(f"Downloaded {self.file_name} from GCP bucket {self.bucket_name} to {RAW_FILE_PATH}.")
            
        except Exception as e:
            logger.error(f"Error downloading file from GCP: {e}")
            raise CustomException("Failed to download file from GCP", sys)
        
    def split_data(self):
        try:
            logger.info("Starting data splitting process.")
            data = pd.read_csv(RAW_FILE_PATH)
            train_data, test_data = train_test_split(data, test_size=1 - self.train_test_ratio, random_state=42)
            train_data.to_csv(TRAIN_FILE_PATH, index=False)
            test_data.to_csv(TEST_FILE_PATH, index=False)
            logger.info(f"Data split into train and test sets with ratio {self.train_test_ratio}.")
            logger.info(f"Train data saved at {TRAIN_FILE_PATH} and test data saved at {TEST_FILE_PATH}.")  
        
        except Exception as e:
            logger.error(f"Error splitting data  from GCP: {e}")
            raise CustomException("Failed to split data file from GCP", sys)

    def run(self):
        try:
            logger.info("Data Ingestion process started.")
            self.download_csv_from_gcp()
            self.split_data()
            logger.info("Data Ingestion process completed successfully.")
        except Exception as ce:
            logger.error(f"Error in Data Ingestion process: {ce}")
            raise CustomException("Data Ingestion process failed", sys)  
        finally:
            logger.info("Data Ingestion process finished.")


if __name__ == "__main__":
    config = read_yaml(CONFIG_PATH)
    data_ingestion = DataIngestion(config)
    data_ingestion.run()
