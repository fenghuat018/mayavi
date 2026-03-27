pipeline {
 agent {
    kubernetes {
      yaml """
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: gcloud
    image: google/cloud-sdk:slim
    command:
    - cat
    tty: true
"""
    }
  }
 
  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Sonar Scan') {
      steps {
        container('gcloud') {
          script {
            def scannerHome = tool 'sonar-scanner'
            sh "${scannerHome}/bin/sonar-scanner"
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
          sh '''
          gcloud dataproc jobs submit hadoop \
            --project teamproject14848 \
            --region us-central1 \
            --cluster hadoop-cluster \
            --jar file:///usr/lib/hadoop-mapreduce/hadoop-mapreduce-examples.jar \
            -- wordcount \
            gs://teamproject14848-shuangxz-bucket/input/input.txt \
            gs://teamproject14848-shuangxz-bucket/output/wordcount-${BUILD_NUMBER}
          '''
        }
      }
    }
  }
}
