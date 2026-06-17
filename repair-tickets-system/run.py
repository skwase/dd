from app.api_fixed import create_app

from app import db
from app.models import User, Ticket, Category, Comment, TicketHistory

app = create_app()



@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'Ticket': Ticket,
        'Category': Category,
        'Comment': Comment,
        'TicketHistory': TicketHistory
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
