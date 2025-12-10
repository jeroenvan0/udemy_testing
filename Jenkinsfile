pipeline{
    agent any

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = "mlops-new-447207"
        GCLOUD_PATH = "/var/jenkins_home/google-cloud-sdk/bin"
    }

    stages{
        stage('Setting up our Virtual Environment and Installing dependancies'){
            steps{
                script{
                    echo 'Setting up our Virtual Environment and Installing dependancies............'
                    sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    '''
                }
            }
        }

        stage('Building and Pushing Docker Image to GCR'){
            steps{
                withCredentials([file(credentialsId: 'gcp-key' , variable : 'GOOGLE_APPLICATION_CREDENTIALS')]){
                    script{
                        echo 'Building and Pushing Docker Image to GCR.............'
                        sh '''
                        # Check if gcloud is available, try to find it
                        if ! command -v gcloud &> /dev/null; then
                            echo "gcloud not found in PATH, checking common locations..."
                            # Try common installation paths
                            for gcloud_path in "/usr/bin/gcloud" "/usr/local/bin/gcloud" "${GCLOUD_PATH}/gcloud" "$HOME/google-cloud-sdk/bin/gcloud"; do
                                if [ -f "$gcloud_path" ] && [ -x "$gcloud_path" ]; then
                                    echo "Found gcloud at: $gcloud_path"
                                    export PATH=$PATH:$(dirname "$gcloud_path")
                                    break
                                fi
                            done
                            
                            # Verify gcloud is now available
                            if ! command -v gcloud &> /dev/null; then
                                echo "ERROR: gcloud command not found. Please install Google Cloud SDK."
                                echo "You can install it by running: curl https://sdk.cloud.google.com | bash"
                                exit 1
                            fi
                        fi
                        
                        echo "Using gcloud at: $(which gcloud)"

                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}

                        gcloud config set project ${GCP_PROJECT}

                        gcloud auth configure-docker --quiet

                        docker build -t gcr.io/${GCP_PROJECT}/ml-project:latest .

                        docker push gcr.io/${GCP_PROJECT}/ml-project:latest 

                        '''
                    }
                }
            }
        }


        stage('Deploy to Google Cloud Run'){
            steps{
                withCredentials([file(credentialsId: 'gcp-key' , variable : 'GOOGLE_APPLICATION_CREDENTIALS')]){
                    script{
                        echo 'Deploy to Google Cloud Run.............'
                        sh '''
                        # Check if gcloud is available, try to find it
                        if ! command -v gcloud &> /dev/null; then
                            echo "gcloud not found in PATH, checking common locations..."
                            # Try common installation paths
                            for gcloud_path in "/usr/bin/gcloud" "/usr/local/bin/gcloud" "${GCLOUD_PATH}/gcloud" "$HOME/google-cloud-sdk/bin/gcloud"; do
                                if [ -f "$gcloud_path" ] && [ -x "$gcloud_path" ]; then
                                    echo "Found gcloud at: $gcloud_path"
                                    export PATH=$PATH:$(dirname "$gcloud_path")
                                    break
                                fi
                            done
                            
                            # Verify gcloud is now available
                            if ! command -v gcloud &> /dev/null; then
                                echo "ERROR: gcloud command not found. Please install Google Cloud SDK."
                                echo "You can install it by running: curl https://sdk.cloud.google.com | bash"
                                exit 1
                            fi
                        fi
                        
                        echo "Using gcloud at: $(which gcloud)"

                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}

                        gcloud config set project ${GCP_PROJECT}

                        gcloud run deploy ml-project \
                            --image=gcr.io/${GCP_PROJECT}/ml-project:latest \
                            --platform=managed \
                            --region=us-central1 \
                            --allow-unauthenticated
                            
                        '''
                    }
                }
            }
        }
        
    }
}