from waitress import serve

from app import create_app


def main():
    app = create_app()
    serve(app, host="0.0.0.0", port=5090)


if __name__ == "__main__":
    main()
