from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import Ticket, Category, Comment, User
from datetime import datetime

api_bp = Blueprint('api', __name__)

@api_bp.route('/tickets', methods=['GET'])
@login_required
def get_tickets():
    tickets = Ticket.query.all() if current_user.is_responsible() else Ticket.query.filter_by(author_id=current_user.id)
    
    return jsonify({
        'status': 'success',
        'count': tickets.count(),
        'tickets': [t.to_dict() for t in tickets]
    })

@api_bp.route('/tickets/<int:ticket_id>', methods=['GET'])
@login_required
def get_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    if not current_user.is_responsible() and ticket.author_id != current_user.id:
        return jsonify({'status': 'error', 'message': 'Access denied'}), 403
    
    return jsonify({
        'status': 'success',
        'ticket': ticket.to_dict()
    })

@api_bp.route('/tickets', methods=['POST'])
@login_required
def create_ticket_api():
    data = request.get_json()
    
    ticket = Ticket(
        title=data.get('title'),
        description=data.get('description'),
        author_id=current_user.id,
        category_id=data.get('category_id'),
        priority=data.get('priority', 'medium')
    )
    
    db.session.add(ticket)
    db.session.commit()
    
    return jsonify({'status': 'success', 'ticket': ticket.to_dict()}), 201

@api_bp.route('/tickets/<int:ticket_id>/status', methods=['PUT'])
@login_required
def update_status(ticket_id):
    if not current_user.is_responsible():
        return jsonify({'status': 'error', 'message': 'Access denied'}), 403
    
    ticket = Ticket.query.get_or_404(ticket_id)
    data = request.get_json()
    
    old_status = ticket.status
    ticket.status = data.get('status', ticket.status)
    ticket.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'status': 'success', 'ticket': ticket.to_dict()})

@api_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    total = Ticket.query.count()
    new = Ticket.query.filter_by(status='new').count()
    in_progress = Ticket.query.filter_by(status='in_progress').count()
    completed = Ticket.query.filter_by(status='completed').count()
    
    return jsonify({
        'total': total,
        'new': new,
        'in_progress': in_progress,
        'completed': completed
    })