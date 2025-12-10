pipeline {
    agent any

    environment {
        VENV_DIR    = 'venv'
        GCP_PROJECT = 'udemy-training-480608'
        GCLOUD_PATH = '/var/jenkins_home/google-cloud-sdk/bin'
    }
    
    stages {
        stage('Cloning github repos to Jenkins') {
            steps {
                script {
                    echo 'Cloning github repo to Jenkins....'
                    checkout scmGit(
                        branches: [[name: '*/main']],
                        extensions: [],
                        userRemoteConfigs: [[
                            credentialsId: 'github-token',
                            url: 'https://github.com/jeroenvan0/udemy_testing'
                        ]]
                    )
                }
            }
        }

        stage('Setting up Python Virtual Environment and installing dependencies') {
            steps {
                script {
                    echo 'Setting up Python Virtual Environment and installing dependencies.....'
                    sh '''
                        python3 -m venv ${VENV_DIR}
                        . ${VENV_DIR}/bin/activate
                        pip install --upgrade pip
                        pip install -e .
                    '''
                }
            }
        }

        stage('Building and pushing docker image to GCR') {
            steps {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo 'Building and pushing docker image to GCR.....'
                        sh '''
                            # Verify gcloud is available
                            if [ ! -f "${GCLOUD_PATH}/gcloud" ]; then
                                echo "ERROR: gcloud not found at ${GCLOUD_PATH}/gcloud"
                                exit 1
                            fi
                            
                            # Use full path to gcloud
                            GCLOUD_CMD="${GCLOUD_PATH}/gcloud"
                            
                            # Verify key file exists and is readable
                            if [ ! -f "${GOOGLE_APPLICATION_CREDENTIALS}" ]; then
                                echo "ERROR: Key file not found at ${GOOGLE_APPLICATION_CREDENTIALS}"
                                exit 1
                            fi
                            
                            echo "Key file path: ${GOOGLE_APPLICATION_CREDENTIALS}"
                            echo "Key file exists: $(test -f ${GOOGLE_APPLICATION_CREDENTIALS} && echo 'yes' || echo 'no')"
                            echo "Key file readable: $(test -r ${GOOGLE_APPLICATION_CREDENTIALS} && echo 'yes' || echo 'no')"
                            
                            # Authenticate with service account
                            ${GCLOUD_CMD} auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                            
                            # Set project
                            ${GCLOUD_CMD} config set project ${GCP_PROJECT}
                            
                            # Configure Docker authentication
                            ${GCLOUD_CMD} auth configure-docker --quiet

                            # Build and push Docker image
                            docker build -t gcr.io/${GCP_PROJECT}/ml-project:latest .
                            docker push gcr.io/${GCP_PROJECT}/ml-project:latest
                        '''
                    }
                }
            }
        }
    }
}
