echo "Waiting for postgres..."

while ! nc -z db $DB_PORT; do
  sleep 0.1
done

echo "PostgreSQL started"

python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

exec "$@"