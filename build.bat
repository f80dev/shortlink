cd app
docker build -t f80hub/shortlinks%1 .
docker push f80hub/shortlinks%1
cd ..
echo "docker rm -f shortlinks && docker pull f80hub/shortlinks%1 && docker run --name shortlinks -ti f80hub/shortlinks%1:latest"

