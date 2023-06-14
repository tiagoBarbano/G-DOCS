Criar Ambiente Virtual:

python3 -m venv venv


Ativar Ambiente Virtual:

source venv/bin/activate

Rodar main.py:
* uvicorn main:app --reload

Comando do Alembic
* Init aliembic:
    * alembic init -t async migrations

* After change the model, this command add new change:
    * alembic revision --autogenerate -m "init"

* To apply the change:
    * alembic upgrade head

* to check
    * alembic check