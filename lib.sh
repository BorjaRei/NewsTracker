sudo apt-get update -y
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install python3.8 -y
sudo apt-get install python3-pip -y
pip install pandas==1.3.5
pip install newsdataapi==0.1.1
pip install sklearn==0.0
pip install transformers==4.15.0
pip install elasticsearch==7.16.2
pip3 install torch==1.8.2+cpu torchvision==0.9.2+cpu torchaudio==0.8.2 -f https://download.pytorch.org/whl/lts/1.8/torch_lts.html
