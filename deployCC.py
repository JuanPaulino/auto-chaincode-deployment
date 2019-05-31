import sys
import subprocess
import json

def getResources():
    with open('./deployResources.json') as json_string_file:
        return json.load(json_string_file)

def setResources(resources, NewChainCodeVersionStr):
    with open('./deployResources.json', 'w') as json_file:
        json.dump(resources, json_file, indent=4)

def deployCC(ChainCodeName, NewChainCodeVersionStr):
    ComandFindOldDockers = [ 'docker', 'ps', '-aqf', 'name='+ChainCodeName ]
    ComandFindOldImages  = [ 'docker', 'images', '-aq', '*'+ChainCodeName+'*' ]
    ComandInstallCC      = [ 'docker', 'exec', '-e', '"CORE_PEER_LOCALMSPID=Org1MSP"', '-e', '"CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp"', 'cli', 'peer', 'chaincode', 'install', '-n', ChainCodeName, '-v', NewChainCodeVersionStr, '-p', '/opt/gopath/src/github.com/'+ChainCodeName, '-l', 'node' ]
    ComandUpdateCC       = [ 'docker', 'exec', '-e', '"CORE_PEER_LOCALMSPID=Org1MSP"', '-e', '"CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp"', 'cli', 'peer', 'chaincode', 'upgrade', '-o', 'orderer.example.com:7050', '-C', 'mychannel', '-n', ChainCodeName, '-l', 'node', '-v', NewChainCodeVersionStr, '-c', '{"Args":[]}' ]

    # Find Old Dockers
    print("> Find old dockers:", " ".join(ComandFindOldDockers))
    resultFindOldDockers = subprocess.run(ComandFindOldDockers, stdout=subprocess.PIPE)
    resultFindOldDockers = resultFindOldDockers.stdout.decode('utf-8').split("\n")

    # Find Old Images
    print("> Find old dockers:", " ".join(ComandFindOldImages))
    resultFindOldImages = subprocess.run(ComandFindOldImages, stdout=subprocess.PIPE)
    resultFindOldImages = resultFindOldImages.stdout.decode('utf-8').split("\n")

    
    for dockerId in resultFindOldDockers:
        if dockerId != '':
            comandDockersStop = [ 'docker', 'stop', dockerId ]
            comandDockersRM = [ 'docker', 'rm', dockerId ]
            # Stop Dockers
            print("> Stop old docker:", " ".join(comandDockersStop))
            subprocess.run(comandDockersStop, stdout=subprocess.PIPE)

            # Remove dockers
            print("> Remove old docker:", " ".join(comandDockersRM))
            subprocess.run(comandDockersRM, stdout=subprocess.PIPE)
    
    for imageId in resultFindOldImages:
        if imageId != '':
            # Remove images
            comandImageRM = [ 'docker', 'rmi', imageId ]
            print("> Remove old images:", " ".join(comandImageRM))
            subprocess.run(comandImageRM, stdout=subprocess.PIPE)

    # Install Docker
    print("> Docker Install:", " ".join(ComandInstallCC))
    subprocess.run(ComandInstallCC)

    # Update Docker
    print("> Docker Update:", " ".join(ComandUpdateCC))
    subprocess.run(ComandUpdateCC)

def main():
    if len(sys.argv) >= 2 and len(sys.argv) <= 3:
        resources = getResources()

        ChainCodeName = sys.argv[1]

        if ChainCodeName in resources:
            VersionComplete = resources[ChainCodeName]["versionCC"].split(".")
            Version         = int(VersionComplete[0])
            Hotfix          = int(VersionComplete[1])

            #If new version argument
            if len(sys.argv) == 3 and sys.argv[2] == 'version++':
                Version += 1
                Hotfix  = 0
            else:
                Hotfix += 1

            NewChainCodeVersionStr = str(Version)+"."+str(Hotfix)

            # Run comands
            deployCC(ChainCodeName, NewChainCodeVersionStr)

            # Set resources
            resources[ChainCodeName]["versionCC"] = NewChainCodeVersionStr

            setResources(resources, NewChainCodeVersionStr)

            print("> New ChainCode Version:" + NewChainCodeVersionStr)
        else:
            print('This ChainCode not exist.')
    else:
        print('Format valid is:')
        print('python deployCC.py name_chain_code version++')
        print('python deployCC.py name_chain_code hotfix++')

main()

#ComandDockerStop = [ 'docker', 'stop', resources[ChainCodeName]["dockerId"] ]
#ComandDockerRM   = [ 'docker', 'rm', resources[ChainCodeName]["dockerId"] ]
#ComandInstallCC  = ['docker', 'exec', '-e', '"CORE_PEER_LOCALMSPID=Org1MSP"', '-e', '"CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp"', 'cli', 'peer', 'chaincode', 'install', '-n', ChainCodeName, '-v', NewChainCodeVersionStr, '-p', '/opt/gopath/src/github.com/'+ChainCodeName, '-l', 'node']
#ComandUpdateCC   = ['docker', 'exec', '-e', '"CORE_PEER_LOCALMSPID=Org1MSP"', '-e', '"CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp"', 'cli', 'peer', 'chaincode', 'upgrade', '-o', 'orderer.example.com:7050', '-C', 'mychannel', '-n', ChainCodeName, '-l', 'node', '-v', NewChainCodeVersionStr, '-c' '{"Args":[]}']
#ComandFindCC   = [ 'docker', 'ps', '-f', 'name='+ChainCodeName+"-"+NewChainCodeVersionStr, '-q' ]
