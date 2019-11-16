# to update requirements run: pip freeze > requirements.txt
# docker image build . -t webapp:0.2.0

FROM python:3.7.5-stretch

LABEL maintainer <jedrzej.kozal@gmail.com>

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "QaA/manage.py", "runserver", "0.0.0.0:8000"]