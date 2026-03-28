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
            set -e

            gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"
            gcloud config set project "$GCP_PROJECT"
            
            gsutil -m rm -r "${REPO_GCS_PATH}" || true
            gsutil -m rm -r "${OUTPUT_GCS_PATH}" || true
            
            WORK_DIR="repo_for_hadoop"
            rm -rf "$WORK_DIR"
            mkdir -p "$WORK_DIR"
            
            find . -type f ! -path "./.git/*" | while read f; do
              rel="${f#./}"
              safe_name=$(echo "$rel" | sed 's#/#__#g')
              cp "$f" "$WORK_DIR/$safe_name"
            done
            
            gsutil -m cp -r "$WORK_DIR" "${REPO_GCS_PATH}"
            
            MASTER_INSTANCE=$(gcloud compute instances list \
              --filter="name ~ ^${DATAPROC_CLUSTER}-m AND zone:(${DATAPROC_ZONE})" \
              --format='value(name)' | head -n 1)
            
            STREAMING_JAR=$(gcloud compute ssh "jenkins@$MASTER_INSTANCE" \
              --zone "$DATAPROC_ZONE" \
              --quiet \
              --command='find /usr/lib -name "hadoop-streaming*.jar" 2>/dev/null | head -n 1' \
              | tail -n 1 | tr -d '\r')
            
            echo "Using streaming jar: $STREAMING_JAR"
            
            gcloud dataproc jobs submit hadoop \
              --project "$GCP_PROJECT" \
              --region "$DATAPROC_REGION" \
              --cluster "$DATAPROC_CLUSTER" \
              --files mapper.py,reducer.py \
              --jar "file://$STREAMING_JAR" \
              -- \
              -mapper "python3 mapper.py" \
              -reducer "python3 reducer.py" \
              -input "${REPO_GCS_PATH}/repo_for_hadoop" \
              -output "${OUTPUT_GCS_PATH}"
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
