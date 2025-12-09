pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = "udemy-training-480608"
        GCLOUD_PATH = "var/jenkins_home/google-cloud-sdk/bin"
    }
    
    stages {
        stage('Cloning github repos to Jenkins'){
            steps {
                script{
                    echo 'Clonning github repo to Jenkins....'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/jeroenvan0/udemy_testing']])
                }
            }
        }

        stage('Setting up Python Virtual Environment and installing depencencies'){
            steps {
                script{
                    echo 'Setting up Python Virtual Environment and installing depencencies.....'
                    sh '''
                        python3 -m venv ${VENV_DIR}
                        . ${VENV_DIR}/bin/activate
                        pip install --upgrade pip
                        pip install -e .
                       '''
                }
            }
        }
         stage('Building and pushing docker image to GCR'){
            steps {
                withCredentials([file(credentialsId: 'gcp-key', variable : 'GOOGLE_APPLICATION_CREDENTIALS')]){
                    script{
                        echo 'Building and pushing docker image to GCR.....'
                        sh '''
                        export PATH=$PATH:$(GCLOUD_PATH)

                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}

                        gcloud config set project ${GCP_PROJECT}

                        gcloud auth configure-docker --quiet

                        docker build -t gcr.io/${GCP-PROJECT}/ml-project:latest .

                        docker push gcr.io/${GCP-PROJECT}/ml-project:latest 
                        
                        '''
                        
                }

            }
        }
    }
}