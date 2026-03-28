pipeline {
 agent {
    kubernetes {
      yaml """
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: sonar
    image: sonarsource/sonar-scanner-cli:latest
    command:
    - cat
    tty: true
  - name: gcloud
    image: google/cloud-sdk:slim
    command:
    - cat
    tty: true
"""
    }
  }

  environment {
    GCP_PROJECT      = 'teamproject-zhang-tong'
    DATAPROC_REGION  = 'us-central1'
    DATAPROC_ZONE    = 'us-central1-a'
    DATAPROC_CLUSTER = 'hadoop-cluster'
    HADOOP_BUCKET    = 'teamproject-zhang-tong-bucket0'

    REPO_GCS_PATH   = "gs://${HADOOP_BUCKET}/repo-src/${BUILD_NUMBER}"
    OUTPUT_GCS_PATH = "gs://${HADOOP_BUCKET}/output/lines-${BUILD_NUMBER}"
  }
 
  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Sonar Scan') {
      steps {
        container('sonar') {
          withSonarQubeEnv('SonarQube') {
            sh 'sonar-scanner'
          }
        }
      }
    }

    stage('Quality Gate') {
      steps {
        timeout(time: 10, unit: 'MINUTES') {
          waitForQualityGate abortPipeline: true
        }
      }
    }
   
    stage('Run Hadoop Line Count Job') {
      steps {
        container('gcloud') {
          withCredentials([file(credentialsId: 'gcp-sa-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
            sh '''
              set -e

              echo "Authenticating to GCP..."
              gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"
              gcloud config set project "$GCP_PROJECT"

              echo "Cleaning old GCS paths if they exist..."
              gsutil -m rm -r "${REPO_GCS_PATH}" || true
              gsutil -m rm -r "${OUTPUT_GCS_PATH}" || true

              echo "Uploading repository to GCS..."
              gsutil -m cp -r . "${REPO_GCS_PATH}"

              echo "Finding Dataproc master instance..."
              MASTER_INSTANCE=$(gcloud compute instances list \
                --filter="name ~ ^${DATAPROC_CLUSTER}-m AND zone:(${DATAPROC_ZONE})" \
                --format='value(name)' | head -n 1)

              if [ -z "$MASTER_INSTANCE" ]; then
                echo "ERROR: Could not find Dataproc master instance."
                exit 1
              fi

              echo "Dataproc master instance: $MASTER_INSTANCE"

              echo "Locating Hadoop streaming jar on Dataproc master..."
              STREAMING_JAR=$(gcloud compute ssh "$MASTER_INSTANCE" \
                --zone "$DATAPROC_ZONE" \
                --quiet \
                --command='find /usr/lib -name "hadoop-streaming*.jar" 2>/dev/null | head -n 1')

              if [ -z "$STREAMING_JAR" ]; then
                echo "ERROR: Could not find hadoop-streaming jar on Dataproc master."
                exit 1
              fi

              echo "Using streaming jar: $STREAMING_JAR"

              echo "Submitting Hadoop Streaming job..."
              gcloud dataproc jobs submit hadoop \
                --project "$GCP_PROJECT" \
                --region "$DATAPROC_REGION" \
                --cluster "$DATAPROC_CLUSTER" \
                --files mapper.py,reducer.py \
                --jar "file://$STREAMING_JAR" \
                -- \
                -mapper "python3 mapper.py" \
                -reducer "python3 reducer.py" \
                -input "${REPO_GCS_PATH}" \
                -output "${OUTPUT_GCS_PATH}"
            '''
          }
        }
      }
    }
  }

  post {
    success {
      echo "Pipeline completed successfully."
      echo "Hadoop output path: ${OUTPUT_GCS_PATH}"
    }
    failure {
      echo "Pipeline failed."
    }
  }
}
