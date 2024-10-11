VENV_DIR=.venv

ifeq ($(OS),Windows_NT)
	ACTIVATE=call $(VENV_DIR)\Scripts\activate
else
	ACTIVATE=source $(VENV_DIR)/bin/activate
endif

dev:
	python bot.py --dev

dev-no-sync:
	python bot.py --dev --no-sync

run:
	python bot.py