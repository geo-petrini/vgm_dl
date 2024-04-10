docker build --pull --rm -f "Dockerfile" -t vgmdl:latest "." 
docker run --volume=vgmdl_download:/app/downloads -p 5000:5000 --restart=no -d vgmdl:latest