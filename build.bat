cd app
docker build -t f80hub/shortlinks%2 .
docker push f80hub/shortlinks%2
cd ..

putty -pw %1 -ssh root@38.242.210.208 -m "install_server"
