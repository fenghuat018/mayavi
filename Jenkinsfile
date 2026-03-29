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

    REPO_GCS_PATH    = "gs://${HADOOP_BUCKET}/repo-src/${BUILD_NUMBER}"
    OUTPUT_GCS_PATH  = "gs://${HADOOP_BUCKET}/output/lines-${BUILD_NUMBER}"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
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
              set -eu
    
              echo "Authenticating to GCP..."
              gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"
              gcloud config set project "$GCP_PROJECT"
    
              # Check grammar
              sed -i 's/\\r$//' mapper.py reducer.py || true
              python3 -m py_compile mapper.py
              python3 -m py_compile reducer.py
    
              STREAMING_JAR="/usr/lib/hadoop/hadoop-streaming.jar"
    
              # avoid overlaping
              SCRIPT_GCS_DIR="gs://${HADOOP_BUCKET}/hadoop-scripts/${BUILD_NUMBER}"
    
              echo "Uploading scripts to: $SCRIPT_GCS_DIR"
              gsutil cp mapper.py "${SCRIPT_GCS_DIR}/mapper.py"
              gsutil cp reducer.py "${SCRIPT_GCS_DIR}/reducer.py"
    
              echo "Submitting Dataproc job..."
              echo "Input:  $REPO_GCS_PATH"
              echo "Output: $OUTPUT_GCS_PATH"
    
              gcloud dataproc jobs submit hadoop \
                --project "$GCP_PROJECT" \
                --region "$DATAPROC_REGION" \
                --cluster "$DATAPROC_CLUSTER" \
                --files "${SCRIPT_GCS_DIR}/mapper.py,${SCRIPT_GCS_DIR}/reducer.py" \
                --jar "file://$STREAMING_JAR" \
                -- \
                -mapper "python3 mapper.py" \
                -reducer "python3 reducer.py" \
                -input "$REPO_GCS_PATH" \
                -output "$OUTPUT_GCS_PATH"
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
