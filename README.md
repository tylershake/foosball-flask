# foosball-flask
Repository for docker container: tjshake/foosball-flask

Build instructions.
docker build --no-cache=true -t "foosball-flask:X.X.X" .
docker tag "image" "dockeruser/image"
docker login
docker push "dockeruser/image"