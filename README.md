### Installation

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Quick start

```shell
docker compose up -d
python test_layer.py
```

### Clean up

```shell
rm generated/*
rm -rf datadir
mkdir datadir
```
