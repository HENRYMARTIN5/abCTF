check:
    mypy abctf --strict
    ruff check --select I --fix .

format:
    ruff format

serve:
    #!python
    import platform
    from os import system
    try:
        match platform.system():
            case "Windows":
                print("You're on Windows. This recipe will still work and serve a WSGI server, but it will not be prod-ready!")
                system('flask --app "abctf.wsgi:app" run')
            case _:
                system('gunicorn "abctf.wsgi:app" --bind 0.0.0.0:8000 --workers 4')
    except KeyboardInterrupt:
        pass