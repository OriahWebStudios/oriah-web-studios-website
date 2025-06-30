from app import create_app

app = create_app()

# Trigger redeploy

if __name__ == '__main__':
    with app.app_context():
        app.run()