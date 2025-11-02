#!/bin/bash

python app.py &
cd frontend
npm run dev &
cd ..
