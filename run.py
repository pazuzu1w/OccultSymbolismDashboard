# run.py
from app import create_app

app = create_app()

if __name__ == '__main__':
    print("╔═══════════════════════════════════════════════════════╗")
    print("║       Occult Symbolism Dashboard Starting Up           ║")
    print("╚═══════════════════════════════════════════════════════╝")
    print("  * Running on http://127.0.0.1:5000")
    print("  * Press CTRL+C to quit")
    app.run(debug=True)