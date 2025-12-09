pipeline {
    agent any

    environement {
        VENV = 'venv'
    }
    
    stages {
        stage('Cloning github repos to Jenkins'){
            steps {
                script{
                    echo 'Clonning github repo to Jenkins....'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/jeroenvan0/udemy_testing']])
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
}