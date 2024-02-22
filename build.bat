cd app
docker build -t f80hub/shortlinks .
docker push f80hub/shortlinks
cd ..

putty -pw %1 -ssh root@38.242.210.208 -m "install_server"
