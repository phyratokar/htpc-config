# SETUP SAMBA
sudo rm /etc/samba/smb.conf
sudo ln -s /home/srv-user/htpc-config/smb.conf /etc/samba/smb.conf
sudo service smbd restart
sudo service nmbd restart

# SETUP FIREWALL
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 137
sudo ufw allow 139
sudo ufw allow 443
sudo ufw allow 53
sudo ufw allow 6789
sudo ufw allow 9091
sudo ufw allow 8989
sudo ufw allow 7878
sudo ufw allow 8686
sudo ufw enable

# INSTALL DOCKER
sudo apt-get update
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
sudo usermod -aG docker $USER
sudo curl -L "https://github.com/docker/compose/releases/download/1.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# PULL DOCKER IMAGES
docker pull linuxserver/nzbget:latest
docker pull linuxserver/transmission:latest
docker pull linuxserver/sonarr:latest
docker pull linuxserver/radarr:latest
docker pull linuxserver/lidarr:latest
docker pull pihole/pihole:latest
docker pull jlesage/handbrake:latest

# DISABLE DNS
sudo systemctl disable systemd-resolved.service
sudo systemctl stop systemd-resolved

# SETUP LIBRARY TRANSCODING
sudo apt-get install libmediainfo0v5 python3-pip
pip3 install pymediainfo
crontab -l > crontab_file
echo "00 02 * * * \"python3 /home/srv-user/htpc-config/transcode_library.py --root_dir=/home/srv-user/media --max_hours=5\"" >> crontab_file
crontab crontab_file
rm crontab_file
