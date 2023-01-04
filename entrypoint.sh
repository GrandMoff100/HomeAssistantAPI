. .venv/bin/activate
python -c "import time; time.sleep($DELAY)"
pytest tests --disable-warnings --cov --cov-report xml:coverage/coverage.xml
