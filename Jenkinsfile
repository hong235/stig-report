pipeline {
    agent any
    stages {
        stage('Non-Parallel Stage') {
            steps {
                checkout([$class: 'GitSCM', branches: [[name: '*/master']], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[url: 'https://services.csa.spawar.navy.mil/bitbucket/scm/cos/simple-java-maven-app.git']]])
            }
        }
        stage('Parallel Stage') {
            /*when {
                branch 'master'
            }*/
            failFast true
            parallel {
                stage('CodeDx') {
                    agent {
                        label "jdk8"
                    }
                    steps {
                        echo "On Branch A"
                        echo "Starting CodeDX Aggregation..."
                        sh '''
prj="luckett-test"
nprefix=""
DATE=$(date '+%Y-%m-%d_%H:%M:%S')
rptName=${nprefix}${prj}CodeDxReport_${DATE}
rptType="xml"
stdType="asdstig"
codeDxServer="https://services.csa.spawar.navy.mil/codedx/api"
postDataJson='{"filter":{"name":"luckett-test"}}'
ApiTokenCodeDx=API-Key:91a6b846-fa7c-4071-a885-231315d7747d
cType='Content-Type: application/json'
jsonFilter='{"filter":{"~status":[3,4,5,6]},"config":{"summaryMode":"simple","detailsMode":"simple","includeComments":false}}'
rptFilter='{"filter":{},"sort":{"by":"id","direction":"ascending"},"pagination":{"page":1,"perPage":10}}'
#--------------------------------------------------------------------------------------------------------------------------------------------------------------
echo $postDataJson | python -m json.tool
echo $jsonFilter | python -m json.tool
prjIdn=$(curl -k -H "$cType" -H "$ApiTokenCodeDx" -X POST "${codeDxServer}/projects/query" --data "${postDataJson}" | python -c "import sys, json; print json.load(sys.stdin)[0]['id']")
jobIdnJson=$(curl -k -H "$cType" -X POST -d "$jsonFilter" -H "$ApiTokenCodeDx" ${codeDxServer}/projects/${prjIdn}/report/csv)
jobIdn=$(echo $jobIdnJson | python -c "import sys, json; print json.load(sys.stdin)['jobId']")
prjIdn=`curl -k -H "Content-Type:application/json" -H "$ApiTokenCodeDx" -X POST "${codeDxServer}/projects/query" --data "${postDataJson}" | python -c "import sys, json; print json.load(sys.stdin)[0]['id']"`
jobSts="queued"
until [  $jobSts == "completed" ];
do
    jobSts=$(curl -k -H "$ApiTokenCodeDx" -X GET "${codeDxServer}/jobs/${jobIdn}" | python -c "import sys, json; print json.load(sys.stdin)['status']" )
    sleep 20s
done
curl -k -H "$cType" -X POST -d "$rptFilter" -H "$ApiTokenCodeDx" ${codeDxServer}/projects/$prjIdn/findings/table
curl -k -o report.csv -H "$cType" -H "$ApiTokenCodeDx" -X GET ${codeDxServer}/jobs/${jobIdn}/result
tail report.csv
sleep 300
python3 /usr/local/bin/STIG-Report/report.py --config /usr/local/bin/STIG-Report/report.ini
fop -fo /usr/local/bin/STIG-Report/example/report.fo -pdf /usr/local/bin/STIG-Report/example/report.pdf
sleep 300
                '''
                    }
                }
                stage('Maven Build') {
                    agent {
                        label "jenkins-build-agent"
                    }
                    steps {
                        checkout([$class: 'GitSCM', branches: [[name: '*/master']], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[url: 'https://services.csa.spawar.navy.mil/bitbucket/scm/cos/simple-java-maven-app.git']]])
                        sh '''
                                ls -al
                                mvn -B clean package
                           '''
                    }
                }
                stage('Checkmarx') {
                    agent {
                        label "jenkins-build-agent"
                    }
                    stages {
                        stage('Nested 1') {
                            steps {
                                echo "In stage Nested 1 within Branch C"
                                //sleep 2000
                                echo "skipping nested branch"
                            }
                        }
                        stage('Nested 2') {
                            steps {
                                echo "skipping cx"
                                //sleep 2000
                                //step([$class: 'CxScanBuilder', comment: '', credentialsId: 'test2', excludeFolders: '', excludeOpenSourceFolders: '', exclusionsSetting: 'global', failBuildOnNewResults: false, failBuildOnNewSeverity: 'HIGH', filterPattern: '', fullScanCycle: 10, includeOpenSourceFolders: '', incremental: true, osaArchiveIncludePatterns: '*.zip, *.war, *.ear, *.tgz', osaInstallBeforeScan: false, password: '{AQAAABAAAAAQIYuW6hbS8dfl5RfpPPkwMe5zoLZv2DM8VEbZbWAQ0MM=}', projectName: 'test2', sastEnabled: true, serverUrl: 'services.csa.spawar.navy.mil/CxWebClient', sourceEncoding: 'Provide Checkmarx server credentials to see source encodings list', username: 'user', vulnerabilityThresholdResult: 'FAILURE', waitForResultsEnabled: true])
                                }
                        }
                    }
                }
            }
        }
    }
}
