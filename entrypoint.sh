. .venv/bin/activate
python -c "import time; time.sleep(60)"
pytest tests --disable-warnings --cov --cov-report xml:coverage/coverage.xml
