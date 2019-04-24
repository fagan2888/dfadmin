pipeline {
    agent any

    stages {
        stage('Git Prepare') {
            steps {
                echo 'Initializing submodules..'
                sh 'make git-submodules-init'
            }
        }
        stage('Build') {
            steps {
                echo 'Building..'
                sh 'docker-compose build'
            }
        }
        stage('Starting') {
            steps {
                echo 'Starting DFAdmin..'
                sh 'docker-compose up -d'
            }
        }
        stage('Test') {
            steps {
                echo 'Testing..'
                sh 'docker-compose up -d'
                sh 'make check || true'
                junit '**/target/*.xml'
            }
        }
        stage('Stopping') {
            steps {
                echo 'Stopping DFAdmin..'
                sh 'docker-compose stop'
            }
        }
        stage('QA') {
            steps {
                echo 'Testing..'
                sh 'make codacy-report'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying....'
            }
        }
    }

}
