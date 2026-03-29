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
              ls -l
              ls -l mapper.py reducer.py
    
              echo "--- python versions ---"
              python3 --version || true
              /usr/bin/python3 --version || true
              which python3 || true
    
              echo "--- sha256 ---"
              sha256sum mapper.py reducer.py || true
    
              echo "--- mapper.py first 40 lines ---"
              sed -n '1,40p' mapper.py
    
              echo "--- reducer.py first 40 lines ---"
              sed -n '1,40p' reducer.py
    
              echo "--- normalize line endings ---"
              sed -i 's/\r$//' mapper.py reducer.py || true
    
              echo "--- python compile check ---"
              python3 -m py_compile mapper.py
              python3 -m py_compile reducer.py
    
              STREAMING_JAR="/usr/lib/hadoop/hadoop-streaming.jar"
    
              echo "Using streaming jar: $STREAMING_JAR"
              echo "Hadoop input path: gs://teamproject-zhang-tong-bucket0/repo-src/23"
              echo "Hadoop output path: $OUTPUT_GCS_PATH"

              echo "Creating debug_mapper.sh..."

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
              sed -i 's/\r$//' debug_mapper.sh mapper.py reducer.py || true
    
              echo "Submitting minimal Hadoop Streaming job..."
             gcloud dataproc jobs submit hadoop \
                --project "$GCP_PROJECT" \
                --region "$DATAPROC_REGION" \
                --cluster "$DATAPROC_CLUSTER" \
                --files "$WORKSPACE/mapper.py,$WORKSPACE/reducer.py,$WORKSPACE/debug_mapper.sh" \
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
