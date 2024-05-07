cd web
call  gh-pages -d . --repo https://github.com/f80dev/shortlink.git -f -t true -b gh-pages -m \"update from gh-pages\""

cd ..

cd app
docker build -t f80hub/shortlinks%2 .
docker push f80hub/shortlinks%2
cd ..

putty -pw %1 -ssh root@93.127.202.181 -m "install_server"
