import os
from pyexpat import model
import pandas as pd
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from config.model_params import *
from utils.common_functions import read_yaml, load_data
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import accuracy_score, classification_report, recall_score, f1_score, precision_score
import joblib
import lightgbm as lgb
from scipy.stats import randint

import mlflow 
import mlflow.sklearn


logger = get_logger(__name__)

class ModelTraining:
    def __init__(self, train_data_path, test_data_path, model_output_path, config_path):
        self.train_data_path = train_data_path
        self.test_data_path = test_data_path
        self.model_output_path = model_output_path
        self.config = read_yaml(config_path)

        self.params_dist = LIGHTBM_PARAMS
        self.random_search_params = RANDOM_SEARCH_PARAMS

    def load_and_split_data(self):
        try:
            logger.info(f"Loading training data from {self.train_data_path}")
            train_df = load_data(self.train_data_path)

            logger.info(f"Loading testing data from {self.test_data_path}")
            test_df = load_data(self.test_data_path)

            X_train = train_df.drop(columns=['booking_status'])
            y_train = train_df['booking_status']

            X_test = test_df.drop(columns=['booking_status'])
            y_test = test_df['booking_status']

            logger.info("Data loaded and split into features and target variable successfully")

            return X_train, y_train, X_test, y_test
        except Exception as e:
            logger.error(f"Error loading and splitting data: {e}")
            raise CustomException("Data Loading and Splitting Failed", e)
        

    def train_lgbm(self, X_train, y_train):
        try:
            logger.info("Initiating LightGBM model training")
            lgb_model = lgb.LGBMClassifier(random_state=self.random_search_params['random_state'])

            logger.info("Starting Randomized Search for hyperparameter tuning")
            random_search = RandomizedSearchCV(
                estimator=lgb_model,
                param_distributions=self.params_dist,
                n_iter=self.random_search_params['n_iter'],
                cv=self.random_search_params['cv'],
                n_jobs=self.random_search_params['n_jobs'],
                verbose=self.random_search_params['verbose'],
                random_state=self.random_search_params['random_state'],
                scoring=self.random_search_params['scoring']
            )
            
            logger.info("Starting our model training")
            random_search.fit(X_train, y_train)
            logger.info("Hyperparameter tuning completed")

            best_params = random_search.best_params_
            best_lgb_model = random_search.best_estimator_

            logger.info(f"Best parameters found: {best_params}")

            return best_lgb_model
        
        except Exception as e:
            logger.error(f"Error during model training: {e}")
            raise CustomException("Model Training Failed", e)
        

    def evaluate_model(self, model, X_test, y_test):
        try:
            logger.info("Evaluating the trained model on test data")
            y_pred = model.predict(X_test)

            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted')
            recall = recall_score(y_test, y_pred, average='weighted')
            f1 = f1_score(y_test, y_pred, average='weighted')

            logger.info(f"Model Evaluation Metrics:\nAccuracy: {accuracy}\nPrecision: {precision}\nRecall: {recall}\nF1 Score: {f1}")       
            return {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1
            }
        except Exception as e:
            logger.error(f"Error during model evaluation: {e}")
            raise CustomException("Model Evaluation Failed", e)

    
    def save_model(self, model):
        try:
            os.makedirs(os.path.dirname(self.model_output_path), exist_ok=True)
            logger.info(f"Saving the trained model to {self.model_output_path}")

            joblib.dump(model, self.model_output_path)
            logger.info("Model saved successfully")

        except Exception as e:
            logger.error(f"Error saving the model: {e}")
            raise CustomException("Model Saving Failed", e)
        

    def run(self):
        try:
            with mlflow.start_run():
                logger.info("Starting model training pipeline")
                logger.info("Starting MLflow experiment tracking")
                logger.info("Logging the training and testing data set to MLFLOW")

                mlflow.log_artifact(self.train_data_path, artifact_path="datasets")
                mlflow.log_artifact(self.test_data_path, artifact_path="datasets")
            
                X_train, y_train, X_test, y_test = self.load_and_split_data()

                best_lgb_model = self.train_lgbm(X_train, y_train)
                metrics = self.evaluate_model(best_lgb_model, X_test, y_test)
                self.save_model(best_lgb_model)

                mlflow.log_artifact(self.model_output_path,artifact_path="models")
                logger.info("Logged the model to MLflow")
                mlflow.log_params(best_lgb_model.get_params())
                logger.info("Logged the model parameters & Metrics to MLflow")
                mlflow.log_metrics(metrics)

                logger.info("Model training pipeline completed successfully")

        except Exception as e:
            logger.error(f"Error in model training pipeline: {e}")
            raise CustomException("Model Training Pipeline Failed", e)
        

if __name__ == "__main__":
    trainer = ModelTraining(
        train_data_path=PROCESSED_TRAIN_DATA_PATH,
        test_data_path=PROCESSED_TEST_DATA_PATH,
        model_output_path=MODEL_OUTPUT_PATH,
        config_path=CONFIG_PATH
    )
    
    trainer.run()

        

        
    






