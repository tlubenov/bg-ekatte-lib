VENV:=venv

$(VENV)/bin/activate:
	python3 -m venv $(VENV)
	./$(VENV)/bin/pip install poetry
	./$(VENV)/bin/poetry install

venv: $(VENV)/bin/activate
#	./$(VENV)/bin/activate

build: venv
	./$(VENV)/bin/poetry build

