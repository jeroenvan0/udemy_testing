pipeline {
    agent any
    
    stages {
        stage('Cloning github repos to Jenkins'){
            steps {
                script{
                    echo 'Clonning github repo to Jenkins....'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/jeroenvan0/udemy_testing']])
                }
        }
    }
}
}