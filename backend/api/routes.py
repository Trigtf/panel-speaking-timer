from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
def status():
    # κρατάμε αυτό απλό: επιστρέφει το ίδιο format με το websocket
    # Επειδή το engine είναι global στο main.py, στο demo αρκεί να δείχνει "ok"
    # Αν θες /status να δείχνει πραγματικά δεδομένα, πες μου να το κάνουμε πιο "καθαρό" με app.state.
    return {"status": "use websocket /ws for live data"}

