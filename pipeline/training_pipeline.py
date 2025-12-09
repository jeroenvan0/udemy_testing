from config.paths_config import PROCESSED_DIR, CONFIG_PATH, TRAIN_FILE_PATH, TEST_FILE_PATH, PROCESSED_TRAIN_DATA_PATH, PROCESSED_TEST_DATA_PATH, MODEL_OUTPUT_PATH
from utils.common_functions import read_yaml, load_data
from src.data_ingestion import DataIngestion
from src.data_preprocessing import DataProcessor
from src.model_training import ModelTraining

if __name__ == "__main__":
    ## 1. DATA INGESTION
    config = read_yaml(CONFIG_PATH)
    data_ingestion = DataIngestion(config)
    data_ingestion.run()

    ## 2. DATA PREPROCESSING
    processor = DataProcessor(
        train_path=TRAIN_FILE_PATH,
        test_path=TEST_FILE_PATH,
        processed_dir=PROCESSED_DIR,
        config_path=CONFIG_PATH
    )
    processor.process()

    ## 3. MODEL TRAINING
    trainer = ModelTraining(
        train_data_path=PROCESSED_TRAIN_DATA_PATH,
        test_data_path=PROCESSED_TEST_DATA_PATH,
        model_output_path=MODEL_OUTPUT_PATH,
        config_path=CONFIG_PATH
    )
    
    trainer.run()

        


  