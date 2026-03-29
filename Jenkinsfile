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
    
              echo "=== workspace debug info ==="
              pwd
              ls -l mapper.py reducer.py
    
              echo "--- normalize line endings ---"
              sed -i 's/\\r$//' mapper.py reducer.py || true
    
              echo "--- create debug_mapper.sh ---"
              cat > debug_mapper.sh <<'EOF'
#!/bin/sh
set -eu
echo "DEBUG: shell started" >&2
echo "DEBUG: pwd=$(pwd)" >&2
echo "DEBUG: ls -l:" >&2
ls -l >&2 || true
echo "DEBUG: which python3=$(command -v python3 || true)" >&2
echo "DEBUG: python3 version:" >&2
python3 --version >&2 || true
echo "DEBUG: running mapper..." >&2
exec python3 mapper.py
EOF
    
              chmod +x debug_mapper.sh
              sed -i 's/\\r$//' debug_mapper.sh || true
    
              echo "--- upload scripts to GCS ---"
              gsutil cp mapper.py gs://teamproject-zhang-tong-bucket0/debug/mapper.py
              gsutil cp reducer.py gs://teamproject-zhang-tong-bucket0/debug/reducer.py
              gsutil cp debug_mapper.sh gs://teamproject-zhang-tong-bucket0/debug/debug_mapper.sh
    
              STREAMING_JAR="/usr/lib/hadoop/hadoop-streaming.jar"
    
              echo "Submitting Hadoop Streaming job..."
    
              gcloud dataproc jobs submit hadoop \
                --project "$GCP_PROJECT" \
                --region "$DATAPROC_REGION" \
                --cluster "$DATAPROC_CLUSTER" \
                --files "gs://teamproject-zhang-tong-bucket0/debug/mapper.py,gs://teamproject-zhang-tong-bucket0/debug/reducer.py,gs://teamproject-zhang-tong-bucket0/debug/debug_mapper.sh" \
                --jar "file://$STREAMING_JAR" \
                -- \
                -mapper "sh debug_mapper.sh" \
                -reducer "python3 reducer.py" \
                -input "gs://teamproject-zhang-tong-bucket0/repo-src/23" \
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
