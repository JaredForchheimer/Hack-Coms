Run this stuff:
#Note - these are linux commands, convert to windows equivalent
#Note - start these commands from root folder
pip install -r requirements.txt 
python -m spacy download en_core_web_sm
cd frontend
npm install
cd ..
#Note, you probably can't run run.sh if you are not on linux, so open, remove ampersands, and run windows equivalent commands
./run.sh
