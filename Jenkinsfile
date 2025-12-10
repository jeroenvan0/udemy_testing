pipeline {
    agent any

    environment {
        VENV_DIR    = 'venv'
        GCP_PROJECT = "mlops-new-447207"
    }

    stages {
        stage('Setup venv & install deps') {
            steps {
                script {
                    echo 'Setting up virtual environment and installing dependencies...'
                    sh """
                        python -m venv ${VENV_DIR}
                        . ${VENV_DIR}/bin/activate
                        pip install --upgrade pip
                        pip install -e .
                    """
                }
            }
        }

        stage('Build & Push Docker image to GCR') {
            steps {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo 'Building and pushing Docker image to GCR...'
                        sh """
                            # Check gcloud
                            if ! command -v gcloud > /dev/null 2>&1; then
                              echo "ERROR: gcloud not found in PATH"
                              exit 1
                            fi

                            echo "Using gcloud at: \$(which gcloud)"
                            gcloud --version

                            # Auth & project
                            gcloud auth activate-service-account --key-file="\${GOOGLE_APPLICATION_CREDENTIALS}"
                            gcloud config set project ${GCP_PROJECT}

                            # Docker auth
                            gcloud auth configure-docker --quiet

                            # Build & push image
                            docker build -t gcr.io/${GCP_PROJECT}/ml-project:latest .
                            docker push gcr.io/${GCP_PROJECT}/ml-project:latest
                        """
                    }
                }
            }
        }

        stage('Deploy to Cloud Run') {
            steps {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo 'Deploying to Cloud Run...'
                        sh """
                            if ! command -v gcloud > /dev/null 2>&1; then
                              echo "ERROR: gcloud not found in PATH"
                              exit 1
                            fi

                            echo "Using gcloud at: \$(which gcloud)"
                            gcloud --version

                            gcloud auth activate-service-account --key-file="\${GOOGLE_APPLICATION_CREDENTIALS}"
                            gcloud config set project ${GCP_PROJECT}

                            gcloud run deploy ml-project \
                                --image=gcr.io/${GCP_PROJECT}/ml-project:latest \
                                --platform=managed \
                                --region=us-central1 \
                                --allow-unauthenticated
                        """
                    }
                }
            }
        }
    }
}
