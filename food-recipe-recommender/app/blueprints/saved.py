from typing import Tuple, Dict, Any
from flask import Blueprint, jsonify, request, Response
from flask_login import login_required, current_user
from .. import db
from ..models import SavedRecipe
import logging


saved_bp = Blueprint('saved', __name__)
logger = logging.getLogger(__name__)


@saved_bp.get('/api/saved-recipes')
@login_required
def get_saved_recipes() -> Tuple[Response, int]:
    try:
        entries = SavedRecipe.query.filter_by(user_id=current_user.user_id).all()
        ids = [e.recipe_id for e in entries]
        logger.debug("[saved] user=%s count=%s", current_user.user_id, len(ids))
        return jsonify({'recipes': [{'id': rid} for rid in ids]})
    except Exception as e:
        return jsonify({'error': f'Failed to get saved recipes: {e}'}), 500


@saved_bp.post('/api/saved-recipes')
@login_required
def save_recipe() -> Tuple[Response, int]:
    data: Dict[str, Any] = request.get_json()
    if not data or 'recipe_id' not in data:
        return jsonify({'error': 'recipe_id is required'}), 400

    recipe_id = str(data['recipe_id']).strip()
    if not recipe_id:
        return jsonify({'error': 'recipe_id cannot be empty'}), 400
    try:
        existing = SavedRecipe.query.filter_by(user_id=current_user.user_id, recipe_id=recipe_id).first()
        if existing:
            return jsonify({'error': 'Recipe already saved'}), 400
        saved = SavedRecipe(user_id=current_user.user_id, recipe_id=recipe_id)
        db.session.add(saved)
        db.session.commit()
        return jsonify({'message': 'Recipe saved successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to save recipe: {e}'}), 500


@saved_bp.delete('/api/saved-recipes/<recipe_id>')
@login_required
def remove_saved(recipe_id: str) -> Tuple[Response, int]:
    try:
        saved = SavedRecipe.query.filter_by(user_id=current_user.user_id, recipe_id=str(recipe_id)).first()
        if not saved:
            return jsonify({'error': 'Recipe not found in saved recipes'}), 404
        db.session.delete(saved)
        db.session.commit()
        return jsonify({'message': 'Recipe removed from saved recipes'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to remove saved recipe: {e}'}), 500

