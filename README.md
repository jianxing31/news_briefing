# News Extract and Summary App

## About
This app can get news from online site and summarize it. To get news from the sites, we need to configure the path of the links we need. Environment for the app is Ubuntu:20.04. Python version is 3.8.  

Sample Output:
![sample.png](https://github.com/jianxing31/news_briefing/blob/master/images/%E3%82%B9%E3%82%AF%E3%83%AA%E3%83%BC%E3%83%B3%E3%82%B7%E3%83%A7%E3%83%83%E3%83%88%202023-08-21%2023.36.54.png)

## Getting Started
### 1. set up environments
- build docker container for the app
```shell
docker build -f Dockerfile -t news_briefing:1 .
```
- run docker container for the app
```shell
docker run -it -d --name news_briefing news_briefing:1 bash
```
```shell
docker start news_briefing
```
- enter the docker container for the app
```shell
docker exec -it news_briefing bash
```
### 2. run the app
```shell
python3 app/main.py
```

### Optional arguments
```shell
  -h, --help           Show help message.
  -t, --task           Task_name file path. Default is "app/task.json"
  -o, --overide      If True and there is alredy a table in db for this
                        task, this table will be overided. Default is False.
```

## What else is done with this repo
All videos in [my youtube channel](https://www.youtube.com/@happy_ltb/videos) were also collected, processed and uploaded with this repo.
![youtube_page.png](https://github.com/jianxing31/news_briefing/blob/master/images/%E3%82%B9%E3%82%AF%E3%83%AA%E3%83%BC%E3%83%B3%E3%82%B7%E3%83%A7%E3%83%83%E3%83%88%202023-08-21%2023.50.24.png)
