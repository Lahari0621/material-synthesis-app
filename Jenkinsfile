pipeline {
    agent any

    environment {
        FLUTTER_IMAGE = 'ghcr.io/cirruslabs/flutter:3.41.5'
        FLUTTER_CONTAINER = 'material-synthesis-flutter-builder'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Flutter Web') {
            steps {
                sh '''
                    set -e

                    echo "Creating Flutter build container..."

                    docker rm -f ${FLUTTER_CONTAINER} 2>/dev/null || true

                    docker create \
                        --name ${FLUTTER_CONTAINER} \
                        ${FLUTTER_IMAGE} \
                        sleep infinity

                    docker start ${FLUTTER_CONTAINER}

                    echo "Copying project into Flutter container..."
                    docker cp . ${FLUTTER_CONTAINER}:/app

                    echo "Running Flutter build..."
                    docker exec ${FLUTTER_CONTAINER} sh -c '
                        cd /app &&
                        flutter pub get &&
                        flutter build web --release
                    '

                    echo "Preparing build output..."
                    docker exec ${FLUTTER_CONTAINER} sh -c \
                        "chown -R 1000:1000 /app/build/web"

                    echo "Preparing Jenkins workspace..."
                    rm -rf build
                    mkdir -p build

                    echo "Copying Flutter web build back..."
                    docker cp ${FLUTTER_CONTAINER}:/app/build/web ./build/

                    echo "Removing temporary Flutter container..."
                    docker rm -f ${FLUTTER_CONTAINER}

                    echo "Flutter web build completed."
                '''
            }
        }

        stage('Build Frontend Image') {
            steps {
                sh '''
                    set -e

                    echo "Building Nginx frontend image..."
                    docker compose build frontend
                '''
            }
        }

        stage('Deploy Frontend') {
            steps {
                sh '''
                    set -e

                    echo "Deploying frontend..."
                    docker compose up -d --no-deps frontend

                    echo "Frontend deployment completed."
                '''
            }
        }
    }

    post {
        success {
            echo 'CI/CD deployment successful.'
            echo 'Website: http://localhost:8080'
        }

        failure {
            echo 'CI/CD deployment failed.'
        }

        always {
            sh '''
                docker rm -f ${FLUTTER_CONTAINER} 2>/dev/null || true
            '''
        }
    }
}
