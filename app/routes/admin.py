# -*- coding: utf-8 -*-
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from app.decorators import admin_required, root_required
from app.extensions import db
from app.forms.admin_media import AdminMediaForm
from app.services.media_service import (
    create_media,
    delete_media,
    get_media,
    list_media_admin_page,
    update_media,
)
from app.services.user_service import deactivate_user, get_user, list_all_users, reactivate_user, set_admin_role

bp = Blueprint("management", __name__, url_prefix="/management")


@bp.route("/media/new", methods=["GET", "POST"])
@admin_required
def add_media():
    """Create a catalogue entry (movies, anime, TV). Admin-only HTML form."""
    form = AdminMediaForm()
    if form.validate_on_submit():
        try:
            media = create_media(
                form.title.data.strip(),
                form.media_type.data,
                **form.to_create_kwargs(),
            )
            flash(f"Created “{media.title}”.", "success")
            return redirect(url_for("main.item_detail", imdb_id=media.imdb_id))
        except ValueError as err:
            flash(str(err), "error")
        except IntegrityError:
            db.session.rollback()
            flash("Could not save: duplicate IMDb ID or another database constraint failed.", "error")

    return render_template("admin/add_media.html", form=form)


@bp.route("/media")
@admin_required
def manage_media():
    """Catalogue table — edit / delete."""
    per_page = 15
    page = request.args.get("page", 1, type=int) or 1
    page = max(page, 1)
    offset = (page - 1) * per_page
    items, total = list_media_admin_page(limit=per_page, offset=offset)
    page_count = (total + per_page - 1) // per_page if total else 0
    if page_count and page > page_count:
        page = page_count
        offset = (page - 1) * per_page
        items, total = list_media_admin_page(limit=per_page, offset=offset)
    return render_template(
        "admin/manage_media.html",
        items=items,
        total=total,
        per_page=per_page,
        page=page,
        offset=offset,
        page_count=page_count,
    )


@bp.route("/media/<int:media_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_media(media_id):
    media = get_media(media_id)
    if not media:
        abort(404)

    form = AdminMediaForm()
    if request.method == "GET":
        form.populate_from_media(media)
    elif form.validate_on_submit():
        try:
            kw = form.to_create_kwargs()
            kw["title"] = form.title.data.strip()
            kw["media_type"] = form.media_type.data
            update_media(media_id, **kw)
            flash("Saved changes.", "success")
            return redirect(url_for("management.manage_media"))
        except ValueError as err:
            flash(str(err), "error")
        except IntegrityError:
            db.session.rollback()
            flash("Could not save (database constraint).", "error")

    return render_template("admin/edit_media.html", form=form, media=media)


@bp.route("/media/<int:media_id>/delete", methods=["POST"])
@admin_required
def remove_media(media_id):
    if not get_media(media_id):
        abort(404)
    delete_media(media_id)
    flash("Media deleted. Watchlist rows for this title were removed.", "success")
    return redirect(url_for("management.manage_media"))


@bp.route("/users", methods=["GET", "POST"])
@admin_required
def manage_users():
    """Manage user accounts. Deactivation is soft-delete and preserves data."""
    if request.method == "POST":
        uid = request.form.get("user_id", type=int)
        action = (request.form.get("action") or "").strip()
        target = get_user(uid, include_deactivated=True) if uid else None
        if not target:
            flash("User not found.", "error")
        elif target.id == current_user.id:
            flash("You cannot deactivate your own account here.", "error")
        elif action == "deactivate":
            if target.is_admin and not current_user.is_root:
                flash("Admins can only deactivate regular user accounts.", "error")
            else:
                try:
                    deactivate_user(target)
                    flash(f"{target.username} has been deactivated.", "success")
                except ValueError as err:
                    flash(str(err), "error")
        elif action == "reactivate":
            try:
                reactivate_user(target)
                flash(f"{target.username} has been reactivated.", "success")
            except ValueError as err:
                flash(str(err), "error")
        else:
            flash("Invalid action.", "error")
        return redirect(url_for("management.manage_users"))

    users = list_all_users(include_deactivated=True, include_root=False)
    return render_template("admin/manage_users.html", users=users)


@bp.route("/admins", methods=["GET", "POST"])
@root_required
def manage_admins():
    """Grant or revoke admin privileges (root only)."""
    if request.method == "POST":
        uid = request.form.get("user_id", type=int)
        action = (request.form.get("action") or "").strip()
        target = get_user(uid, include_deactivated=True) if uid else None
        if not target:
            flash("User not found.", "error")
        elif target.is_root:
            flash("The root account cannot be changed here.", "error")
        elif action == "grant":
            set_admin_role(target, is_admin=True)
            flash(f"{target.username} is now an administrator.", "success")
        elif action == "revoke":
            try:
                set_admin_role(target, is_admin=False)
                flash(f"Administrator role removed from {target.username}.", "success")
            except ValueError as err:
                flash(str(err), "error")
        else:
            flash("Invalid action.", "error")
        return redirect(url_for("management.manage_admins"))

    users = list_all_users(include_deactivated=False, include_root=True)
    return render_template("admin/manage_admins.html", users=users)
