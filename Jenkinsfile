pipeline {
    agent {
        kubernetes {
            yaml '''
            apiVersion: v1
            kind: Pod
            spec:
              containers:
              - name: python
                image: python:3.10-slim
                command:
                - cat
                tty: true
              - name: docker
                image: docker:20.10.16-dind
                command:
                - cat
                tty: true
                privileged: true
                volumeMounts:
                - name: docker-sock
                  mountPath: /var/run/docker.sock
              - name: kubectl
                image: bitnami/kubectl:latest
                command:
                - cat
                tty: true
              volumes:
              - name: docker-sock
                hostPath:
                  path: /var/run/docker.sock
            '''
        }
    }
    
    environment {
        DOCKER_REGISTRY = 'docker.io/mtrivedi1410'
        IMAGE_NAME = 'intelliview-backend'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        LLM_SERVICE_URL = credentials('llm-service-url')
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                container('python') {
                    sh 'pip install -r intelliview_backend/requirements.txt'
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                container('python') {
                    dir('intelliview_backend/intelliview') {
                        sh 'python manage.py test'
                    }
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                container('docker') {
                    dir('intelliview_backend') {
                        sh 'docker build -t ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} .'
                    }
                }
            }
        }
        
        stage('Push Docker Image') {
            steps {
                container('docker') {
                    withCredentials([usernamePassword(credentialsId: 'DockerHubCredential', passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                        sh 'echo $DOCKER_PASSWORD | docker login docker.io -u $DOCKER_USERNAME --password-stdin'
                        sh 'docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}'
                    }
                }
            }
        }
        
        stage('Deploy to Kubernetes') {
            steps {
                container('kubectl') {
                    // Create ConfigMap for env variables
                    sh '''
                    cat <<EOF | kubectl apply -f -
                    apiVersion: v1
                    kind: ConfigMap
                    metadata:
                      name: intelliview-backend-config
                      namespace: intelliview
                    data:
                      LLM_SERVICE_URL: "${LLM_SERVICE_URL}"
                    EOF
                    '''
                    
                    // Apply the Kubernetes manifests with proper image and environment
                    sh '''
                    cat <<EOF | kubectl apply -f -
                    apiVersion: apps/v1
                    kind: Deployment
                    metadata:
                      name: intelliview-backend
                      namespace: intelliview
                    spec:
                      replicas: 2
                      selector:
                        matchLabels:
                          app: intelliview-backend
                      template:
                        metadata:
                          labels:
                            app: intelliview-backend
                        spec:
                          containers:
                          - name: intelliview-backend
                            image: ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
                            ports:
                            - containerPort: 8000
                            env:
                            - name: DEBUG
                              value: "False"
                            - name: DJANGO_SECRET_KEY
                              valueFrom:
                                secretKeyRef:
                                  name: intelliview-secrets
                                  key: django-secret-key
                            - name: LLM_SERVICE_URL
                              valueFrom:
                                configMapKeyRef:
                                  name: intelliview-backend-config
                                  key: LLM_SERVICE_URL
                            resources:
                              limits:
                                cpu: "500m"
                                memory: "512Mi"
                              requests:
                                cpu: "200m"
                                memory: "256Mi"
                    ---
                    apiVersion: v1
                    kind: Service
                    metadata:
                      name: intelliview-backend-service
                      namespace: intelliview
                    spec:
                      selector:
                        app: intelliview-backend
                      ports:
                      - port: 80
                        targetPort: 8000
                      type: ClusterIP
                    EOF
                    '''
                    
                    // Wait for deployment to be ready
                    sh 'kubectl rollout status deployment/intelliview-backend -n intelliview --timeout=300s'
                }
            }
        }
    }
    
    post {
        always {
            container('docker') {
                sh 'docker logout ${DOCKER_REGISTRY}'
            }
        }
        success {
            echo 'Backend pipeline completed successfully!'
        }
        failure {
            echo 'Backend pipeline failed!'
        }
    }
} 