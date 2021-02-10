FROM python:3

ADD bot.py /
ADD requirements.txt /
ADD ./data/emojis.json /data/

RUN cd data
RUN ls -a
RUN cd ..

RUN pip install -r requirements.txt

CMD ["python", "./bot.py"]
