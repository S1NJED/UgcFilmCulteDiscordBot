VENV_DIR=.venv

ifeq ($(OS),Windows_NT)
	ACTIVATE=call $(VENV_DIR)\Scripts\activate
else
	ACTIVATE=source $(VENV_DIR)/bin/activate
endif

dev:
	python src/bot.py --dev

run:
	python src/bot.py