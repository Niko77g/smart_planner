from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def main_page():
    return """
<!DOCTYPE html>
<html lang="sk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Study Planner</title>
    <style>
        * {
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, sans-serif;
        }
        body {
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        h1 {
            color: white;
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .subtitle {
            color: rgba(255,255,255,0.9);
            text-align: center;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        .card h2 {
            margin-top: 0;
            color: #5a67d8;
            border-bottom: 3px solid #5a67d8;
            padding-bottom: 10px;
            font-size: 1.4em;
        }
        .card p {
            color: #666;
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin: 12px 0 5px;
            font-weight: 600;
            color: #444;
        }
        input, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 15px;
            transition: border-color 0.3s;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #5a67d8;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 14px 30px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            margin-top: 20px;
            width: 100%;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        .result {
            margin-top: 20px;
            padding: 20px;
            border-radius: 10px;
            display: none;
        }
        .result.success {
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border: 2px solid #28a745;
            color: #155724;
        }
        .result.error {
            background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
            border: 2px solid #dc3545;
            color: #721c24;
        }
        .two-col {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .prediction-box {
            text-align: center;
            padding: 25px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            margin: 15px 0;
            color: white;
        }
        .prediction-box .main-time {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .prediction-box .details {
            font-size: 1.1em;
            opacity: 0.95;
        }
        .prediction-box .daily {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid rgba(255,255,255,0.3);
            font-size: 1.2em;
        }
        .info-box {
            background: #e8f4f8;
            border-left: 4px solid #5a67d8;
            padding: 15px;
            margin: 15px 0;
            border-radius: 0 8px 8px 0;
            font-size: 0.9em;
            color: #555;
        }
        .event-card {
            padding: 15px;
            margin: 10px 0;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #5a67d8;
        }
        .event-card strong {
            color: #5a67d8;
        }
        @media (max-width: 600px) {
            .two-col {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <h1>Smart Study Planner</h1>
    <p class="subtitle">Naplánuj si učenie pomocou umelej inteligencie</p>

    <!-- SEKCIA 1: Predikcia -->
    <div class="card">
        <h2>Odhad casu na ucenie</h2>
        <p>Zisti kolko casu ti zaberie naucit sa dany material. ML model analyzuje obtiaznost, pocet stran a cas do testu.</p>

        <div class="info-box">
            <strong>Ako to funguje?</strong> Model bol natrénovany na realnych datach o tom, kolko casu studentom trvalo naucit sa rozne materialy. Na zaklade tvojich vstupov predikuje celkovy cas potrebny na zvladnutie latky.
        </div>

        <form id="predictForm">
            <div class="two-col">
                <div>
                    <label>Predmet</label>
                    <select name="subject" required>
                        <option value="">-- Vyber predmet --</option>
                        <option value="matematika">Matematika</option>
                        <option value="fyzika">Fyzika</option>
                        <option value="chemia">Chemia</option>
                        <option value="biologia">Biologia</option>
                        <option value="historia">Historia</option>
                        <option value="anglictina">Anglictina</option>
                        <option value="informatika">Informatika</option>
                        <option value="slovensky jazyk">Slovensky jazyk</option>
                        <option value="geografia">Geografia</option>
                    </select>
                </div>
                <div>
                    <label>Typ ulohy</label>
                    <select name="task_type" required>
                        <option value="">-- Vyber typ --</option>
                        <option value="citanie">Citanie / Teoria</option>
                        <option value="cvicenia">Cvicenia / Priklady</option>
                        <option value="opakovanie">Opakovanie</option>
                        <option value="pisanie">Pisanie / Esej</option>
                        <option value="programovanie">Programovanie</option>
                        <option value="projekt">Projekt</option>
                        <option value="slovicka">Slovicka</option>
                        <option value="gramatika">Gramatika</option>
                    </select>
                </div>
            </div>

            <div class="two-col">
                <div>
                    <label>Obtiaznost (1 = lahke, 5 = tazke)</label>
                    <select name="difficulty" required>
                        <option value="1">1 - Velmi lahke</option>
                        <option value="2">2 - Lahke</option>
                        <option value="3" selected>3 - Stredne</option>
                        <option value="4">4 - Tazke</option>
                        <option value="5">5 - Velmi tazke</option>
                    </select>
                </div>
                <div>
                    <label>Pocet stran materialu</label>
                    <input type="number" name="pages_count" min="1" max="500" value="10" required>
                </div>
            </div>

            <label>Kolko dni mas do testu?</label>
            <input type="number" name="days_until_test" min="1" max="365" value="7" required>

            <button type="submit">Vypocitaj cas</button>
        </form>

        <div id="predictResult" class="result"></div>
    </div>

    <!-- SEKCIA 2: Smart event -->
    <div class="card">
        <h2>Vytvor studijny plan v kalendari</h2>
        <p>ML model vypocita cas a automaticky vytvori udalost v tvojom Google kalendari.</p>

        <form id="smartForm">
            <div class="two-col">
                <div>
                    <label>Predmet</label>
                    <select name="subject" required>
                        <option value="">-- Vyber predmet --</option>
                        <option value="matematika">Matematika</option>
                        <option value="fyzika">Fyzika</option>
                        <option value="chemia">Chemia</option>
                        <option value="biologia">Biologia</option>
                        <option value="historia">Historia</option>
                        <option value="anglictina">Anglictina</option>
                        <option value="informatika">Informatika</option>
                    </select>
                </div>
                <div>
                    <label>Typ ulohy</label>
                    <select name="task_type" required>
                        <option value="">-- Vyber typ --</option>
                        <option value="citanie">Citanie / Teoria</option>
                        <option value="cvicenia">Cvicenia / Priklady</option>
                        <option value="opakovanie">Opakovanie</option>
                        <option value="pisanie">Pisanie / Esej</option>
                        <option value="programovanie">Programovanie</option>
                    </select>
                </div>
            </div>

            <div class="two-col">
                <div>
                    <label>Obtiaznost</label>
                    <select name="difficulty" required>
                        <option value="1">1 - Velmi lahke</option>
                        <option value="2">2 - Lahke</option>
                        <option value="3" selected>3 - Stredne</option>
                        <option value="4">4 - Tazke</option>
                        <option value="5">5 - Velmi tazke</option>
                    </select>
                </div>
                <div>
                    <label>Pocet stran</label>
                    <input type="number" name="pages_count" min="1" value="10" required>
                </div>
            </div>

            <label>Dni do testu</label>
            <input type="number" name="days_until_test" min="1" value="7" required>

            <div class="two-col">
                <div>
                    <label>Datum, kedy chces studovat</label>
                    <input type="date" name="study_date" required>
                </div>
                <div>
                    <label>Cas zaciatku</label>
                    <input type="time" name="start_time" value="14:00" required>
                </div>
            </div>

            <button type="submit">Vytvor udalost v kalendari</button>
        </form>

        <div id="smartResult" class="result"></div>
    </div>

    <!-- SEKCIA 3: Manual event -->
    <div class="card">
        <h2>Manualne pridat udalost</h2>
        <p>Pridaj vlastnu udalost bez ML predikcie.</p>

        <form id="manualForm">
            <label>Nazov udalosti</label>
            <input type="text" name="title" placeholder="Napr. Ucenie matematiky" required>

            <label>Datum</label>
            <input type="date" name="date" required>

            <div class="two-col">
                <div>
                    <label>Zaciatok</label>
                    <input type="time" name="start" required>
                </div>
                <div>
                    <label>Koniec</label>
                    <input type="time" name="end" required>
                </div>
            </div>

            <button type="submit">Pridat udalost</button>
        </form>

        <div id="manualResult" class="result"></div>
    </div>

    <!-- SEKCIA 4: Zoznam eventov -->
    <div class="card">
        <h2>Tvoje udalosti</h2>
        <button onclick="loadEvents()" style="margin-top: 0;">Nacitat udalosti</button>
        <div id="eventsList" style="margin-top: 15px;"></div>
    </div>

    <script>
        // Nastav dnesny datum
        const today = new Date().toISOString().split('T')[0];
        document.querySelectorAll('input[type="date"]').forEach(el => {
            el.value = today;
        });

        // PREDIKCIA
        document.getElementById('predictForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const form = e.target;
            const resultDiv = document.getElementById('predictResult');

            const data = {
                subject: form.subject.value,
                task_type: form.task_type.value,
                difficulty: parseInt(form.difficulty.value),
                pages_count: parseInt(form.pages_count.value),
                days_until_test: parseInt(form.days_until_test.value)
            };

            try {
                const res = await fetch('/events/predict', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });

                if (res.ok) {
                    const result = await res.json();
                    resultDiv.className = 'result success';
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = `
                        <div class="prediction-box">
                            <div class="main-time">${result.formatted}</div>
                            <div class="details">
                                Celkovy cas na naucenie: <strong>${result.predicted_minutes} minut</strong>
                            </div>
                            <div class="daily">
                                Pri ${result.days_until_test} dnoch do testu:<br>
                                <strong>~${result.daily_minutes} minut denne</strong>
                            </div>
                        </div>
                        <div class="info-box" style="margin-top: 15px;">
                            <strong>Co to znamena?</strong><br>
                            Na zvladnutie tohto materialu budes potrebovat celkovo ${result.predicted_minutes} minut. 
                            Ak budes studovat kazdy den, staci ti venovat tomu priblizne ${result.daily_minutes} minut denne.
                        </div>
                    `;
                } else {
                    const err = await res.json();
                    showError(resultDiv, err.detail);
                }
            } catch (err) {
                showError(resultDiv, err.message);
            }
        });

        // SMART EVENT
        document.getElementById('smartForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const form = e.target;
            const resultDiv = document.getElementById('smartResult');

            const data = {
                subject: form.subject.value,
                task_type: form.task_type.value,
                difficulty: parseInt(form.difficulty.value),
                pages_count: parseInt(form.pages_count.value),
                days_until_test: parseInt(form.days_until_test.value),
                study_date: form.study_date.value,
                start_time: form.start_time.value + ':00'
            };

            try {
                const res = await fetch('/events/smart', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });

                if (res.ok) {
                    const result = await res.json();
                    resultDiv.className = 'result success';
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = `
                        <div class="event-card">
                            <strong>Udalost vytvorena!</strong><br><br>
                            <strong>${result.title}</strong><br>
                            Datum: ${result.date}<br>
                            Cas: ${result.start} - ${result.end}<br>
                            Trvanie: ${result.predicted_minutes} minut<br>
                            <small style="color: #888;">ID: ${result.event_id}</small>
                        </div>
                        <div class="info-box">
                            Udalost bola pridana do tvojho Google kalendara. Otvor si kalendar a over, ze je tam.
                        </div>
                    `;
                } else {
                    const err = await res.json();
                    showError(resultDiv, err.detail);
                }
            } catch (err) {
                showError(resultDiv, err.message);
            }
        });

        // MANUAL EVENT
        document.getElementById('manualForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const form = e.target;
            const resultDiv = document.getElementById('manualResult');

            const data = {
                title: form.title.value,
                date: form.date.value,
                start: form.start.value + ':00',
                end: form.end.value + ':00'
            };

            try {
                const res = await fetch('/events', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });

                if (res.ok) {
                    const result = await res.json();
                    resultDiv.className = 'result success';
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = `
                        <div class="event-card">
                            <strong>Udalost vytvorena!</strong><br>
                            ${result.title}<br>
                            <small style="color: #888;">ID: ${result.id}</small>
                        </div>
                    `;
                } else {
                    const err = await res.json();
                    showError(resultDiv, err.detail);
                }
            } catch (err) {
                showError(resultDiv, err.message);
            }
        });

        // LOAD EVENTS
        async function loadEvents() {
            const listDiv = document.getElementById('eventsList');
            listDiv.innerHTML = '<p style="color: #666;">Nacitavam...</p>';

            try {
                const res = await fetch('/events');
                if (res.ok) {
                    const events = await res.json();
                    if (events.length === 0) {
                        listDiv.innerHTML = '<p style="color: #666;">Ziadne nadchadzajuce udalosti.</p>';
                    } else {
                        listDiv.innerHTML = events.map(e => `
                            <div class="event-card">
                                <strong>${e.title || 'Bez nazvu'}</strong><br>
                                <small>${e.start} - ${e.end}</small>
                            </div>
                        `).join('');
                    }
                } else {
                    listDiv.innerHTML = '<p style="color: #dc3545;">Chyba pri nacitani.</p>';
                }
            } catch (err) {
                listDiv.innerHTML = `<p style="color: #dc3545;">${err.message}</p>`;
            }
        }

        function showError(div, message) {
            div.className = 'result error';
            div.style.display = 'block';
            div.innerHTML = `<strong>Chyba:</strong> ${message}`;
        }
    </script>
</body>
</html>
    """