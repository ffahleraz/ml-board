# ml-board (Re: ml-dash-board)

A simple dashboard to run classification pipelines.

## Running Locally

### Backend

- Install [anaconda](https://www.anaconda.com/distribution/)
- Create and activate conda environment:
```
$ conda env create -f environment.yml
$ source activate ml-board
```
- Run the backend server:
```
$ cd backend
$ export FLASK_APP=mlboard
$ export FLASK_ENV=development
$ flask run
```

### Frontend

- Make sure you have `node` and `npm` installed
- Run the frontend dev server:
```
$ cd frontend/ml-board
$ npm install
$ npm start
```
- You can access the app on http://localhost:3000/
