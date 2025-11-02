#!/bin/bash

python app.py &
cd frontend
npm run dev &
cd ..

#windows version
# python app.py
#Make new terminal window
#cd frontend
#npm run dev