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
    HADOOP_BUCKET    = 'teamproject-zhang-tong-shuangxz-bucket'
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
   
    stage('Run Hadoop Job') {
      steps {
        container('gcloud') {
          withCredentials([file(credentialsId: 'gcp-sa-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
            sh '''
              gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"
              gcloud config set project "$GCP_PROJECT"
              gcloud auth list
              gcloud config list project

              gcloud dataproc jobs submit hadoop \
                --project "$GCP_PROJECT" \
                --region "$DATAPROC_REGION" \
                --cluster "$DATAPROC_CLUSTER" \
                --jar file:///usr/lib/hadoop-mapreduce/hadoop-mapreduce-examples.jar \
                -- wordcount \
                gs://${HADOOP_BUCKET}/input/input.txt \
                gs://${HADOOP_BUCKET}/output/wordcount-${BUILD_NUMBER}
            '''
          }
        }
      }
    }
  }
}
