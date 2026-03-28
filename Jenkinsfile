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
    DATAPROC_CLUSTER = 'hadoop-cluster'
    HADOOP_BUCKET    = 'teamproject-zhang-tong-bucket0'
    REPO_GCS_PATH    = "gs://${HADOOP_BUCKET}/repo-src/${BUILD_NUMBER}"
    OUTPUT_GCS_PATH  = "gs://${HADOOP_BUCKET}/output/lines-${BUILD_NUMBER}"
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

              gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"
              gcloud config set project "$GCP_PROJECT"

              # Clean old path
              gsutil -m rm -r "${REPO_GCS_PATH}" || true
              gsutil -m rm -r "${OUTPUT_GCS_PATH}" || true

              # Upload the repo to GCS
              gsutil -m cp -r . "${REPO_GCS_PATH}"

              # Submit Hadoop Streaming task
              gcloud dataproc jobs submit hadoop \
                --project "$GCP_PROJECT" \
                --region "$DATAPROC_REGION" \
                --cluster "$DATAPROC_CLUSTER" \
                --files mapper.py,reducer.py \
                --jar file:///usr/lib/hadoop-mapreduce/hadoop-streaming-*.jar
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
}
