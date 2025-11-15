from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def main_page():
    return """
    <!doctype html>
    <html>
    <h1>Smart Planner</h1>
    <form method="post" action="/events" onsubmit="event.preventDefault(); send();">
      <input name="title" placeholder="title" />
      <input name="date" placeholder="YYYY-MM-DD" />
      <input type="time" name="start" required />
      <input type="time" name="end" required" />
      <button type="submit">Create</button>
    </form>
    <script>
    async function send(){
      const f = document.querySelector('form');
      const body = {
        title: f.title.value,
        date: f.date.value,
        start: f.start.value + ":00",
        end: f.end.value + ":00" 
      };
      const r = await fetch('/events', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
      alert('status: ' + r.status);
    }
    </script>
    </html>
    """