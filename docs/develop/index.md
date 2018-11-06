title: Quickstart

```shell
git clone https://github.com/nmlorg/ntelebot
cd ntelebot
virtualenv -ppython3 .
. bin/activate
pip install -e . -r requirements-dev.txt
pytest
cd ..
git clone https://github.com/nmlorg/metabot
cd metabot
virtualenv -ppython3 .
. bin/activate
pip install -e . -r requirements-dev.txt
pytest
```
