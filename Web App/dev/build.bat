

setlocal
call C:\Users\aidan\miniconda3\condabin\conda.bat activate webapp
call cd C:\Users\aidan\Desktop\DjangoServer\CapstoneWeb
call python manage.py migrate
call python manage.py populate
call python manage.py runserver 0.0.0.0:8000
endlocal


