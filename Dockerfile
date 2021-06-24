
FROM python:3

ADD ./ /

RUN pip install bs4
RUN pip install requests
RUN pip install retrying
RUN pip install lxml

CMD [ "python3", "./all_data.py" ]