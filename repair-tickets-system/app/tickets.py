from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Ticket, Category, Comment, TicketHistory, User
from datetime import datetime

tickets_bp = Blueprint('tickets', __name__)


def _build_ticket_detail_payload(ticket_id: int):
    """Render ticket detail partial for AJAX updates."""
    ticket = Ticket.query.get_or_404(ticket_id)
    responsible_users = User.query.filter(User.role.in_(['responsible', 'admin'])).all()
    categories = Category.query.all()
    now = datetime.utcnow()

    # Патч: возвращаем HTML фрагмент, чтобы не перезагружать страницу целиком
    updated_html = render_template(
        'ticket_detail.html',
        ticket=ticket,
        responsible_users=responsible_users,
        categories=categories,
        now=now,
    )

    return {"ok": True, "ticket_id": ticket_id, "updated_html": updated_html}


@tickets_bp.route('/')
@login_required
def list_tickets():
    status_filter = request.args.get('status', 'all')
    category_filter = request.args.get('category', 'all')
    search_query = request.args.get('search', '')
    
    query = Ticket.query
    
    if not current_user.is_responsible():
        query = query.filter_by(author_id=current_user.id)
    
    if status_filter != 'all':
        # Исправлено: in_progress вместо inprogress
        query = query.filter_by(status=status_filter)
    
    if category_filter != 'all' and category_filter.isdigit():
        query = query.filter_by(category_id=int(category_filter))
    
    if search_query:
        query = query.filter(
            (Ticket.title.contains(search_query)) | 
            (Ticket.description.contains(search_query))
        )
    
    tickets = query.order_by(Ticket.created_at.desc()).all()
    categories = Category.query.all()
    
    return render_template('tickets.html', 
                         tickets=tickets, 
                         categories=categories,
                         current_filter=status_filter,
                         current_category=category_filter,
                         search_query=search_query)

@tickets_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_ticket():
    categories = Category.query.all()
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category_id = request.form.get('category_id')
        priority = request.form.get('priority', 'medium')
        
        if not title:
            flash('Название заявки обязательно', 'danger')
            return redirect(url_for('tickets.create_ticket'))
        
        ticket = Ticket(
            title=title,
            description=description,
            author_id=current_user.id,
            category_id=int(category_id) if category_id and category_id.isdigit() else None,
            priority=priority
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        # Добавляем запись в историю
        history = TicketHistory(
            ticket_id=ticket.id,
            field_name='created',
            new_value='Заявка создана'
        )
        db.session.add(history)
        db.session.commit()
        
        flash(f'Заявка #{ticket.id} успешно создана!', 'success')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket.id))
    
    return render_template('create_ticket.html', categories=categories)

@tickets_bp.route('/<int:ticket_id>')
@login_required
def view_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    if not current_user.is_responsible() and ticket.author_id != current_user.id:
        flash('У вас нет доступа к этой заявке', 'danger')
        return redirect(url_for('tickets.list_tickets'))
    
    responsible_users = User.query.filter(User.role.in_(['responsible', 'admin'])).all()
    categories = Category.query.all()
    
    # Добавляем now для шаблона
    from datetime import datetime
    now = datetime.utcnow()
    
    return render_template('ticket_detail.html', 
                         ticket=ticket, 
                         responsible_users=responsible_users,
                         categories=categories,
                         now=now)

@tickets_bp.route('/<int:ticket_id>/edit', methods=['POST'])
@login_required
def edit_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    if not current_user.is_responsible() and ticket.author_id != current_user.id:
        flash('У вас нет прав на редактирование', 'danger')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket.id))

    action = request.form.get('action')

    if action == 'change_status':
        new_status = request.form.get('status')
        old_status = ticket.status
        ticket.status = new_status

        history = TicketHistory(
            ticket_id=ticket.id,
            field_name='status',
            old_value=old_status,
            new_value=new_status
        )
        db.session.add(history)
        flash(f'Статус изменён на "{new_status}"', 'success')
    
    elif action == 'assign_executor':
        assignee_id = request.form.get('assignee_id')
        old_assignee = ticket.assignee.username if ticket.assignee else None
        ticket.assignee_id = int(assignee_id) if assignee_id and assignee_id.isdigit() else None
        new_assignee = ticket.assignee.username if ticket.assignee else None

        history = TicketHistory(
            ticket_id=ticket.id,
            field_name='assignee',
            old_value=old_assignee,
            new_value=new_assignee
        )
        db.session.add(history)
        flash('Исполнитель назначен', 'success')
    
    elif action == 'change_category':
        category_id = request.form.get('category_id')
        old_category = ticket.category.name if ticket.category else None
        ticket.category_id = int(category_id) if category_id and category_id.isdigit() else None
        new_category = ticket.category.name if ticket.category else None

        history = TicketHistory(
            ticket_id=ticket.id,
            field_name='category',
            old_value=old_category,
            new_value=new_category
        )
        db.session.add(history)
        flash('Категория изменена', 'success')
    
    elif action == 'change_priority':
        new_priority = request.form.get('priority')
        old_priority = ticket.priority
        ticket.priority = new_priority

        history = TicketHistory(
            ticket_id=ticket.id,
            field_name='priority',
            old_value=old_priority,
            new_value=new_priority
        )
        db.session.add(history)
        flash('Приоритет изменён', 'success')
    
    elif action == 'add_comment':
        comment_text = request.form.get('comment')
        if comment_text and comment_text.strip():
            comment = Comment(
                content=comment_text,
                ticket_id=ticket.id,
                user_id=current_user.id
            )
            db.session.add(comment)
            
            history = TicketHistory(
                ticket_id=ticket.id,
                field_name='comment',
                new_value=f'Добавлен комментарий: {comment_text[:50]}'
            )
            db.session.add(history)
            flash('Комментарий добавлен', 'success')

    elif action == 'delete_ticket':
        # Удалять может только ответственный/админ (или автор, если понадобится — но сейчас запрещаем)
        if not current_user.is_responsible():
            flash('У вас нет прав на удаление', 'danger')
            return redirect(url_for('tickets.view_ticket', ticket_id=ticket.id))

        history = TicketHistory(
            ticket_id=ticket.id,
            field_name='deleted',
            old_value=ticket.title,
            new_value=f'Удалено пользователем {current_user.username}'
        )
        db.session.add(history)
        db.session.delete(ticket)
        db.session.commit()
        flash('Заявка удалена', 'success')
        return redirect(url_for('tickets.list_tickets'))

    ticket.updated_at = datetime.utcnow()
    db.session.commit()

    return redirect(url_for('tickets.view_ticket', ticket_id=ticket.id))


@tickets_bp.route('/<int:ticket_id>/edit_ajax', methods=['POST'])
@login_required
def edit_ticket_ajax(ticket_id):
    """AJAX version of edit_ticket to avoid full page navigation."""

    ticket = Ticket.query.get_or_404(ticket_id)

    if not current_user.is_responsible() and ticket.author_id != current_user.id:
        return jsonify({"ok": False, "message": "У вас нет прав на редактирование"}), 403

    action = request.form.get('action')

    if action == 'change_status':
        new_status = request.form.get('status')
        old_status = ticket.status
        ticket.status = new_status

        history = TicketHistory(
            ticket_id=ticket.id,
            field_name='status',
            old_value=old_status,
            new_value=new_status,
        )
        db.session.add(history)
        message = f'Статус изменён на "{new_status}"'

    elif action == 'assign_executor':
        assignee_id = request.form.get('assignee_id')
        old_assignee = ticket.assignee.username if ticket.assignee else None
        ticket.assignee_id = int(assignee_id) if assignee_id and assignee_id.isdigit() else None
        new_assignee = ticket.assignee.username if ticket.assignee else None

        history = TicketHistory(
            ticket_id=ticket.id,
            field_name='assignee',
            old_value=old_assignee,
            new_value=new_assignee,
        )
        db.session.add(history)
        message = 'Исполнитель назначен'

    elif action == 'change_category':
        category_id = request.form.get('category_id')
        old_category = ticket.category.name if ticket.category else None
        ticket.category_id = int(category_id) if category_id and category_id.isdigit() else None
        new_category = ticket.category.name if ticket.category else None

        history = TicketHistory(
            ticket_id=ticket.id,
            field_name='category',
            old_value=old_category,
            new_value=new_category,
        )
        db.session.add(history)
        message = 'Категория изменена'

    elif action == 'change_priority':
        new_priority = request.form.get('priority')
        old_priority = ticket.priority
        ticket.priority = new_priority

        history = TicketHistory(
            ticket_id=ticket.id,
            field_name='priority',
            old_value=old_priority,
            new_value=new_priority,
        )
        db.session.add(history)
        message = 'Приоритет изменён'

    elif action == 'add_comment':
        comment_text = request.form.get('comment')
        if not (comment_text and comment_text.strip()):
            return jsonify({"ok": False, "message": "Комментарий не должен быть пустым"}), 400

        comment = Comment(
            content=comment_text,
            ticket_id=ticket.id,
            user_id=current_user.id,
        )
        db.session.add(comment)

        history = TicketHistory(
            ticket_id=ticket.id,
            field_name='comment',
            new_value=f'Добавлен комментарий: {comment_text[:50]}',
        )
        db.session.add(history)
        message = 'Комментарий добавлен'

    elif action == 'delete_ticket':
        if not current_user.is_responsible():
            return jsonify({"ok": False, "message": "У вас нет прав на удаление"}), 403

        history = TicketHistory(
            ticket_id=ticket.id,
            field_name='deleted',
            old_value=ticket.title,
            new_value=f'Удалено пользователем {current_user.username}',
        )
        db.session.add(history)
        db.session.delete(ticket)
        db.session.commit()

        return jsonify({"ok": True, "message": 'Заявка удалена', "redirect": url_for('tickets.list_tickets')}), 200

    else:
        return jsonify({"ok": False, "message": 'Неизвестное действие'}), 400

    ticket.updated_at = datetime.utcnow()
    db.session.commit()

    payload = _build_ticket_detail_payload(ticket_id)
    payload["message"] = message
    return jsonify(payload), 200

