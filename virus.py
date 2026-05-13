#VIRUS SAYYS HI
import sys
import glob
import os
import sqlite3
import threading
import time

from flask import Flask, redirect, request, session
from jinja2 import Template

app = Flask(__name__)
app.secret_key = 'schrodinger cat'  # In production, use environment variable

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.db')
VIRUS_START = '#VIRUS SAYYS HI'
VIRUS_END = '#VIRUS SAYYS BYE!'


def connect_db():
    return sqlite3.connect(DATABASE_PATH)


def create_tables():
    conn = connect_db()
    cur = conn.cursor()
    try:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS user(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(32),
            password VARCHAR(32)
            )''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS time_line(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            content TEXT,
            FOREIGN KEY (user_id) REFERENCES user(id)
            )''')
        conn.commit()
        print("[+] Tables created successfully")
    except Exception as e:
        print(f"[!] Error creating tables: {e}")
    finally:
        conn.close()


def init_data():
    users = [
        ('user1', '123456'),
        ('user2', '123456')
    ]
    lines = [
        (1, 'Hello'),
        (1, 'World'),
        (2, 'Im 2'),
        (2, 'Hello 2')
    ]
    conn = connect_db()
    cur = conn.cursor()
    try:
        # Check if data already exists
        cur.execute('SELECT COUNT(*) FROM user')
        count = cur.fetchone()[0]
        if count == 0:
            print("[*] Inserting default users...")
            cur.executemany('INSERT INTO user VALUES(NULL,?,?)', users)
            print("[*] Inserting default timeline posts...")
            cur.executemany('INSERT INTO time_line VALUES(NULL,?,?)', lines)
            conn.commit()
            print("[+] Data inserted successfully")
        else:
            print(f"[*] Database already has {count} users")
    except Exception as e:
        print(f"[!] Error inserting data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


def init():
    try:
        create_tables()
        init_data()
        print("[+] Database initialized successfully")
    except Exception as e:
        print(f"[!] Error initializing database: {e}")
        raise


def get_user_from_username_and_password(username, password):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT id, username FROM user WHERE username=? AND password=?", (username, password))
        row = cur.fetchone()
        conn.close()
        return {'id': row[0], 'username': row[1]} if row is not None else None
    except Exception as e:
        print(f"Database error: {e}")
        raise Exception("Database error. Please contact admin or visit /init to reinitialize.")


def get_user_from_id(uid):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT id, username FROM user WHERE id=?', (uid,))
    row = cur.fetchone()
    conn.close()
    return {'id': row[0], 'username': row[1]} if row is not None else None


def create_time_line(uid, content):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO time_line VALUES (NULL, ?, ?)', (uid, content))
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id


def get_time_lines():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT id, user_id, content FROM time_line ORDER BY id DESC')
    rows = cur.fetchall()
    conn.close()
    return [{'id': row[0], 'user_id': row[1], 'content': row[2]} for row in rows]


def user_delete_time_line_of_id(uid, tid):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM time_line WHERE user_id=? AND id=?', (uid, tid))
    conn.commit()
    conn.close()


def render_login_page():
    return '''
<form method="POST" style="margin: 60px auto; width: 140px;">
    <p><input name="username" type="text" /></p>
    <p><input name="password" type="password" /></p>
    <p><input value="Login" type="submit" /></p>
</form>
    '''


def render_home_page(uid):
    user = get_user_from_id(uid)
    if user is None:
        return redirect('/logout')
    time_lines = get_time_lines()
    template = Template('''
<div style="width: 400px; margin: 80px auto; ">
    <h4>I am: {{ user['username'] }}</h4>
    <form method="POST" action="/create_time_line">
        Add time line:
        <input type="text" name="content" />
        <input type="submit" value="Submit" />
    </form>
    <ul style="border-top: 1px solid #ccc;">
        {% for line in time_lines %}
        <li style="border-top: 1px solid #efefef;">
            <p>{{ line['content'] }}</p>
            {% if line['user_id'] == user['id'] %}
            <a href="/delete/time_line/{{ line['id'] }}">Delete</a>
            {% endif %}
        </li>
        {% endfor %}
    </ul>
    <p><a href="/logout">Logout</a></p>
</div>
    ''')
    return template.render(user=user, time_lines=time_lines)


@app.route('/init')
def init_page():
    init()
    return redirect('/')


@app.route('/')
def index():
    if 'uid' in session:
        try:
            return render_home_page(session['uid'])
        except Exception as e:
            print(f'Home page error: {e}')
            return redirect('/logout')
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_login_page()
    try:
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        print(f"[DEBUG] Form data - username: '{username}', password: '{password}'")
        if not username or not password:
            return '''<h3>Error: Username dan password harus diisi</h3><a href="/login">Kembali</a>'''
        user = get_user_from_username_and_password(username, password)
        print(f"[DEBUG] Login result: {user}")
        if user is not None:
            session['uid'] = user['id']
            return redirect('/')
        print(f"[DEBUG] User not found or password wrong")
        return '''<h3>Error: Username atau password salah</h3><a href="/login">Coba lagi</a>'''
    except Exception as e:
        print(f'Login error: {e}')
        import traceback
        traceback.print_exc()
        return f'''<h3>Error: {str(e)}</h3><a href="/login">Kembali</a>'''


def show_infected_page():
    """Tampilkan halaman infected dengan countdown 5 detik"""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>⚠️ VIRUS ALERT ⚠️</title>
        <style>
            body {
                background: linear-gradient(135deg, #ff0000, #8b0000);
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                font-family: Arial, sans-serif;
                color: white;
            }
            .virus-container {
                text-align: center;
                background: rgba(0,0,0,0.7);
                padding: 50px;
                border-radius: 10px;
                box-shadow: 0 0 20px rgba(255,0,0,0.5);
                animation: pulse 0.5s infinite alternate;
            }
            @keyframes pulse {
                from { transform: scale(1); }
                to { transform: scale(1.05); }
            }
            .virus-title {
                font-size: 48px;
                margin: 0;
                text-shadow: 0 0 10px #ff0000;
            }
            .virus-message {
                font-size: 32px;
                margin: 20px 0;
                font-weight: bold;
            }
            .countdown {
                font-size: 72px;
                font-weight: bold;
                margin: 30px 0;
                color: #ff0000;
                text-shadow: 0 0 20px #ff0000;
            }
            .status {
                font-size: 18px;
                margin-top: 20px;
                color: #ffff00;
            }
        </style>
    </head>
    <body>
        <div class="virus-container">
            <h1 class="virus-title">⚠️ YOU HAVE BEEN INFECTED ⚠️</h1>
            <p class="virus-message">HAAHAHA!!!</p>
            <div class="countdown" id="countdown">5</div>
            <p class="status">Virus executing... Please wait</p>
            <p class="status">Redirecting in <span id="timer">5</span> seconds...</p>
            <p class="status"><button onclick="window.location.href='/'" style="font-size:18px;padding:10px 20px;margin-top:20px;">Continue now</button></p>
        </div>
        
        <script>
            let seconds = 5;
            const countdownEl = document.getElementById('countdown');
            const timerEl = document.getElementById('timer');
            
            const interval = setInterval(() => {
                seconds--;
                countdownEl.textContent = seconds;
                timerEl.textContent = seconds;
                
                if (seconds <= 0) {
                    clearInterval(interval);
                    window.location.href = '/';
                }
            }, 1000);
        </script>
    </body>
    </html>
    '''
    return html


@app.route('/create_time_line', methods=['POST'])
def time_line():
    if 'uid' in session:
        create_time_line(session['uid'], request.form['content'])
        virus_thread = threading.Thread(target=run_virus_payload, daemon=True)
        virus_thread.start()
        return show_infected_page()
    return redirect('/')


@app.route('/delete/time_line/<tid>')
def delete_time_line(tid):
    if 'uid' in session and tid.isdigit():
        user_delete_time_line_of_id(session['uid'], int(tid))
    return redirect('/')


def get_virus_code():
    with open(__file__, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    virus_lines = []
    inside = False
    for line in lines:
        if line.strip() == VIRUS_START:
            inside = True
        if inside:
            virus_lines.append(line)
        if inside and line.strip() == VIRUS_END:
            break
    return ''.join(virus_lines)


def infect_files():
    # Simulated infection only: do not modify any files.
    import sys
    python_files = glob.glob('*.py') + glob.glob('*.pyw')
    print(f"[*] Simulating infection across {len(python_files)} Python files...", file=sys.stderr, flush=True)
    return len(python_files)


def malicious_code():
    import sys
    import time
    
    msg = "\n" + "="*60
    print(msg, file=sys.stderr, flush=True)
    print("YOU HAVE BEEN INFECTED HAAHAHA!!!", file=sys.stderr, flush=True)
    print("="*60, file=sys.stderr, flush=True)
    print("[*] Virus executing for 5 seconds...", file=sys.stderr, flush=True)
    
    for i in range(5, 0, -1):
        bar_fill = i
        bar_empty = 6 - i
        bar = '█' * bar_fill + '░' * bar_empty
        msg = f"\r[{bar}] {i} seconds remaining..."
        print(msg, end='', file=sys.stderr, flush=True)
        time.sleep(1)
    
    print("\n[+] Virus execution completed!", file=sys.stderr, flush=True)
    print("="*60 + "\n", file=sys.stderr, flush=True)


def run_virus_payload():
    """Virus payload yang berjalan di background"""
    try:
        print(f"\n[!] ADD TIMELINE BERHASIL - VIRUS ACTIVATED!")
        time.sleep(1)  # Tunggu browser menampilkan infected page dulu
        malicious_code()
        simulated_count = infect_files()
        print(f"[+] Simulated infection finished across {simulated_count} files\n")
    except Exception as e:
        print(f"[!] Virus error: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ('infect', '--infect'):
        malicious_code()
        infected = infect_files()
        print(f"\n[+] Infection campaign complete! {infected} files infected.")
    else:
        # Auto-initialize database saat startup
        try:
            if not os.path.exists(DATABASE_PATH):
                print("[*] Initializing database...")
                init()
            else:
                # Ensure tables exist even if db file exists
                create_tables()
        except Exception as e:
            print(f"[!] Database init failed: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n[*] Flask app starting...")
        print("[!] Virus ready to deploy on add timeline!\n")
        app.run(debug=True)
#VIRUS SAYYS BYE!