pipeline {
  agent any

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Sonar Scan') {
      steps {
        withSonarQubeEnv('sonarqube') {
          script {
            def scannerHome = tool 'SonarScanner'
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
  }
}
