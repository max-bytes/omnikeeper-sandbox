# omnikeeper-sandbox-python

## Requirements

* Python 3.10

## Development Setup

### prerequisites

* a running omnikeeper-stack: <https://github.com/max-bytes/omnikeeper-stack>
* recommended: omnikeeper-client-python next to root folder (relative from this README file: ../../omnikeeper-client-python)

### create virtual environment (optional)

```bash
python3.10 -m venv venv
```

### enter virtual environment (optional)

```bash
source ./venv/bin/activate
```

### install requirements

```bash
pip3 install -r requirements.txt
```

### Use local client-library

```bash
pip install -e ../../omnikeeper-client-python
```

## Run

```bash
OAUTHLIB_INSECURE_TRANSPORT=1 python test.py
```

* OAUTHLIB_INSECURE_TRANSPORT is only required when keycloak/auth is configured via http, not https
