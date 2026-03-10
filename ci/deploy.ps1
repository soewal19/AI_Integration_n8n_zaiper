param(
    [string]$ImageName = "health-monitor"
)

python -m unittest discover -s tests -p "test_*.py" -v
docker build -t $ImageName .

if ($env:DOCKER_REGISTRY -and $env:DOCKER_USERNAME -and $env:DOCKER_PASSWORD) {
    docker login $env:DOCKER_REGISTRY -u $env:DOCKER_USERNAME -p $env:DOCKER_PASSWORD
    docker tag $ImageName "$($env:DOCKER_REGISTRY)/$ImageName:latest"
    docker push "$($env:DOCKER_REGISTRY)/$ImageName:latest"
}

