pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'intelliview-backend'
        DOCKER_TAG = "${BUILD_NUMBER}"
        SUPABASE_URL = credentials('SUPABASE_URL')
        SUPABASE_KEY = credentials('SUPABASE_KEY')
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                dir('intelliview_backend') {
                    sh '''
                        python -m venv venv
                        . venv/bin/activate
                        pip install -r requirements.txt
                    '''
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                dir('intelliview_backend') {
                    sh '''
                        . venv/bin/activate
                        python manage.py test
                    '''
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                dir('intelliview_backend') {
                    sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                }
            }
        }
        
        stage('Deploy') {
            steps {
                script {
                    // Stop existing container if running
                    sh "docker stop ${DOCKER_IMAGE} || true"
                    sh "docker rm ${DOCKER_IMAGE} || true"
                    
                    // Run new container with Supabase environment variables
                    sh """
                        docker run -d --name ${DOCKER_IMAGE} \
                        -p 8000:8000 \
                        -e SUPABASE_URL=${SUPABASE_URL} \
                        -e SUPABASE_KEY=${SUPABASE_KEY} \
                        ${DOCKER_IMAGE}:${DOCKER_TAG}
                    """
                }
            }
        }
    }
    
    post {
        failure {
            emailext body: 'Backend build failed. Please check Jenkins for details.',
                     subject: 'Backend Build Failure',
                     to: '${EMAIL_RECIPIENTS}'
        }
        always {
            dir('intelliview_backend') {
                sh 'rm -rf venv'
            }
        }
    }
} 