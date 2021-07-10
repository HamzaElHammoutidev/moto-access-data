
FROM python:3

ADD ./ /

RUN pip install bs4
RUN pip install requests
RUN pip install retrying
RUN pip install lxml
#RUN pip install mysqlclient
#RUN pip install pymysql
#RUN pip install mysql-connector-python



CMD [ "python3", "./link_extract.py" ]