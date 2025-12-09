import os
import sys
import pandas as pd
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import TRAIN_FILE_PATH, TEST_FILE_PATH, PROCESSED_DIR, PROCESSED_TRAIN_DATA_PATH, PROCESSED_TEST_DATA_PATH, CONFIG_PATH
from utils.common_functions import load_data, read_yaml
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE

logger = get_logger(__name__)

class DataProcessor:

    def __init__(self, train_path, test_path, processed_dir, config_path):
        self.train_path = train_path
        self.test_path = test_path
        self.processed_dir = processed_dir 

        self.config = read_yaml(config_path)

        if not os.path.exists(self.processed_dir):
            os.makedirs(self.processed_dir, exist_ok=True)

    
    def preprocess_data(self, df):
        try:
            logger.info("Starting data preprocessing")
            logger.info("Dropping the columns")

            df.drop(columns=['Booking_ID'], inplace=True)
            df.drop_duplicates(inplace=True)

            cat_cols = self.config["data_processing"]['categorical_columns']
            num_cols = self.config["data_processing"]['numerical_columns']

            logger.info("Encoding categorical columns")
            label_encoder = LabelEncoder()
            mappings = {}

            for col in cat_cols:
                df[col] = label_encoder.fit_transform(df[col])
                mappings[col] = dict(zip(label_encoder.classes_, label_encoder.transform(label_encoder.classes_)))

            logger.info("Label mappings are printed below:")
            for col, mapping in mappings.items():
                logger.info(f"{col}: {mapping}")

            logger.info("Skewness handling")
            
            skewness_threshold = self.config["data_processing"]['skewness_threshold']
            skewness = df[num_cols].apply(lambda x: x.skew())
            
            for column in skewness[skewness> abs(skewness_threshold)].index:
                df[column] = np.log1p(df[column])
            
            return df   
        
        except Exception as e:
            logger.error(f"Error during data preprocessing: {e}")
            raise CustomException("Data Preprocessing Failed", e)
        

    def balance_data(self, df):
        try:
            logger.info("Starting data balancing using SMOTE")
            X = df.drop('booking_status', axis=1)
            y = df['booking_status']

            smote = SMOTE(random_state=42)
            X_resampled, y_resampled = smote.fit_resample(X, y)

            balanced_df = pd.concat([X_resampled, y_resampled], axis=1)
            logger.info("Data balancing completed")
            return balanced_df

        except Exception as e:
            logger.error(f"Error during data balancing: {e}")
            raise CustomException("Data Balancing Failed", e)
        
    
    def select_features(self, df):
        try:
            logger.info("Starting feature selection using Random Forest")

            X = df.drop('booking_status', axis=1)
            y = df['booking_status']

            rf = RandomForestClassifier(random_state=42)
            rf.fit(X, y)

            feature_importances = pd.Series(rf.feature_importances_, index=X.columns)
            feature_importances = feature_importances.sort_values(ascending=False)

            top_features = self.config["data_processing"]['no_of_features']
            selected_features = feature_importances.head(top_features).index.tolist()

            logger.info(f"Top {top_features} features selected: {selected_features}")

            top_10_df = df[selected_features + ['booking_status']]
            return top_10_df

        except Exception as e:
            logger.error(f"Error during feature selection: {e}")
            raise CustomException("Feature Selection Failed", e)
        
    def save_data(self, df, file_path):
        try:
            logger.info(f"Saving data to {file_path}")
            df.to_csv(file_path, index=False)
            logger.info(f"Data saved successfully at {file_path}")
        except Exception as e:
            logger.error(f"Error saving data to {file_path}: {e}")
            raise CustomException("Failed to save data", e)
        
    def process(self):
        try:
            logger.info("Loading data from RAW directory")
            train_df = load_data(self.train_path)
            test_df = load_data(self.test_path)

            train_df = self.preprocess_data(train_df)
            test_df = self.preprocess_data(test_df)

            train_df = self.balance_data(train_df)
            test_df = self.balance_data(test_df)

            train_df = self.select_features(train_df)
            test_df = test_df[train_df.columns]

            self.save_data(train_df, PROCESSED_TRAIN_DATA_PATH)
            self.save_data(test_df, PROCESSED_TEST_DATA_PATH)

            logger.info("Data processing completed successfully")

        except Exception as e:
            logger.error(f"Error during data processing: {e}")
            raise CustomException("Data Processing Failed", e)
        
if __name__ == "__main__":

    processor = DataProcessor(
        train_path=TRAIN_FILE_PATH,
        test_path=TEST_FILE_PATH,
        processed_dir=PROCESSED_DIR,
        config_path=CONFIG_PATH
    )
    processor.process()