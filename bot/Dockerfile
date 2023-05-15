FROM python:3.10

# install pip
RUN python -m pip install --upgrade pip

# install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy source code
COPY . .

STOPSIGNAL SIGTERM

# run the app
CMD ["python", "main.py"]