FROM python:3

ADD bot.py /
ADD requirements.txt /
ADD data/emojis.json /

RUN pip install -r requirements.txt

CMD ["python", "./bot.py"]
