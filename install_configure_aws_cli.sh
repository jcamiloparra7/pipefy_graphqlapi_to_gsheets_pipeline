curl -o awscli.zip https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip
unzip -q awscli.zip
sudo ./aws/install
(echo $AWS_ACCESS_KEY_ID; echo $AWS_SECRET_ACCESS_KEY; echo us-east-1; echo json) | aws configure