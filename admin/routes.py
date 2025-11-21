from admin.__init__ import admin_bp
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required

from models import db, User
from auth import admin_required

@admin_bp.route('/')
@login_required
@admin_required
def admin():
    return render_template('admin_dashboard.html')

@admin_bp.route('/promote-user')
@login_required
@admin_required
def promote_user():
    users = User.query.filter(User.user_type != 'admin').all()
    return render_template('admin_promote_user.html', users=users)

@admin_bp.route('/promote-user', methods=['POST'])
@login_required
@admin_required
def promote_user_submit():
    user_id = request.form.get('user_id')

    if not user_id:
        flash("No user selected.", "error")
        return redirect(url_for('pages.promote_user'))

    user = User.query.get_or_404(user_id)

    # Promote to admin
    user.user_type = 'admin'
    db.session.commit()

    flash(f"User '{user.username}' promoted to admin.", "success")
    return redirect(url_for('pages.promote_user'))


@admin_bp.route('/remove-user')
@login_required
@admin_required
def remove_user():
    users = User.query.filter(User.user_type != 'admin').all()
    return render_template('admin_remove_users.html', users=users)

@admin_bp.route('/remove-user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def remove_user_submit(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User removed.")
    return redirect(url_for('admin.remove_user'))


@admin_bp.route('/make-admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def make_admin(user_id):
    user = User.query.get_or_404(user_id)
    user.user_type = 'admin'
    db.session.commit()
    flash("User promoted to admin.")
    return redirect(url_for('admin.promote_user'))

