from flask import Blueprint, jsonify, request
from src.models.user import User, ProgressEntry, db
from src.routes.auth import token_required
from datetime import datetime, timedelta
import json

progress_bp = Blueprint('progress', __name__)

@progress_bp.route('/progress', methods=['POST'])
@token_required
def add_progress_entry(current_user):
    try:
        data = request.json
        
        # Validar fecha
        entry_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        
        # Verificar si ya existe una entrada para esta fecha
        existing_entry = ProgressEntry.query.filter_by(
            user_id=current_user.id,
            date=entry_date
        ).first()
        
        if existing_entry:
            # Actualizar entrada existente
            existing_entry.weight = data.get('weight', existing_entry.weight)
            existing_entry.body_fat_percentage = data.get('body_fat_percentage', existing_entry.body_fat_percentage)
            existing_entry.measurements = json.dumps(data.get('measurements', {}))
            existing_entry.notes = data.get('notes', existing_entry.notes)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Progreso actualizado exitosamente',
                'entry': existing_entry.to_dict()
            }), 200
        else:
            # Crear nueva entrada
            progress_entry = ProgressEntry(
                user_id=current_user.id,
                date=entry_date,
                weight=data.get('weight'),
                body_fat_percentage=data.get('body_fat_percentage'),
                measurements=json.dumps(data.get('measurements', {})),
                notes=data.get('notes')
            )
            
            db.session.add(progress_entry)
            db.session.commit()
            
            return jsonify({
                'message': 'Progreso registrado exitosamente',
                'entry': progress_entry.to_dict()
            }), 201
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@progress_bp.route('/progress', methods=['GET'])
@token_required
def get_progress_entries(current_user):
    try:
        # Parámetros de consulta
        days = request.args.get('days', 30, type=int)
        start_date = datetime.now().date() - timedelta(days=days)
        
        entries = ProgressEntry.query.filter(
            ProgressEntry.user_id == current_user.id,
            ProgressEntry.date >= start_date
        ).order_by(ProgressEntry.date.desc()).all()
        
        return jsonify({
            'entries': [entry.to_dict() for entry in entries],
            'summary': calculate_progress_summary(entries)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@progress_bp.route('/progress/stats', methods=['GET'])
@token_required
def get_progress_stats(current_user):
    try:
        # Obtener entradas de los últimos 90 días
        start_date = datetime.now().date() - timedelta(days=90)
        entries = ProgressEntry.query.filter(
            ProgressEntry.user_id == current_user.id,
            ProgressEntry.date >= start_date
        ).order_by(ProgressEntry.date.asc()).all()
        
        if not entries:
            return jsonify({
                'message': 'No hay datos de progreso disponibles',
                'stats': {}
            }), 200
        
        # Calcular estadísticas
        stats = {
            'weight_change': calculate_weight_change(entries),
            'body_fat_change': calculate_body_fat_change(entries),
            'consistency': calculate_consistency(entries),
            'trends': calculate_trends(entries)
        }
        
        return jsonify({
            'stats': stats,
            'chart_data': prepare_chart_data(entries)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@progress_bp.route('/progress/<int:entry_id>', methods=['DELETE'])
@token_required
def delete_progress_entry(current_user, entry_id):
    try:
        entry = ProgressEntry.query.filter_by(
            id=entry_id,
            user_id=current_user.id
        ).first()
        
        if not entry:
            return jsonify({'error': 'Entrada de progreso no encontrada'}), 404
        
        db.session.delete(entry)
        db.session.commit()
        
        return jsonify({'message': 'Entrada eliminada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def calculate_progress_summary(entries):
    """Calcula un resumen del progreso"""
    if not entries:
        return {}
    
    latest_entry = entries[0]
    oldest_entry = entries[-1]
    
    summary = {
        'total_entries': len(entries),
        'latest_weight': latest_entry.weight,
        'latest_body_fat': latest_entry.body_fat_percentage,
        'date_range': {
            'start': oldest_entry.date.isoformat(),
            'end': latest_entry.date.isoformat()
        }
    }
    
    # Calcular cambios si hay múltiples entradas
    if len(entries) > 1:
        if latest_entry.weight and oldest_entry.weight:
            summary['weight_change'] = round(latest_entry.weight - oldest_entry.weight, 1)
        
        if latest_entry.body_fat_percentage and oldest_entry.body_fat_percentage:
            summary['body_fat_change'] = round(latest_entry.body_fat_percentage - oldest_entry.body_fat_percentage, 1)
    
    return summary

def calculate_weight_change(entries):
    """Calcula el cambio de peso"""
    weight_entries = [e for e in entries if e.weight is not None]
    if len(weight_entries) < 2:
        return None
    
    first_weight = weight_entries[-1].weight
    last_weight = weight_entries[0].weight
    
    return {
        'total_change': round(last_weight - first_weight, 1),
        'percentage_change': round(((last_weight - first_weight) / first_weight) * 100, 1),
        'average_weekly_change': round((last_weight - first_weight) / len(weight_entries) * 7, 2)
    }

def calculate_body_fat_change(entries):
    """Calcula el cambio de grasa corporal"""
    bf_entries = [e for e in entries if e.body_fat_percentage is not None]
    if len(bf_entries) < 2:
        return None
    
    first_bf = bf_entries[-1].body_fat_percentage
    last_bf = bf_entries[0].body_fat_percentage
    
    return {
        'total_change': round(last_bf - first_bf, 1),
        'percentage_points_change': round(last_bf - first_bf, 1)
    }

def calculate_consistency(entries):
    """Calcula la consistencia en el registro"""
    if not entries:
        return 0
    
    # Calcular días entre primera y última entrada
    date_range = (entries[0].date - entries[-1].date).days + 1
    consistency_percentage = (len(entries) / date_range) * 100
    
    return min(round(consistency_percentage, 1), 100)

def calculate_trends(entries):
    """Calcula tendencias en los datos"""
    if len(entries) < 3:
        return {}
    
    # Tendencia de peso (últimas 3 entradas)
    recent_weights = [e.weight for e in entries[:3] if e.weight is not None]
    weight_trend = 'stable'
    if len(recent_weights) >= 2:
        if recent_weights[0] > recent_weights[-1]:
            weight_trend = 'increasing'
        elif recent_weights[0] < recent_weights[-1]:
            weight_trend = 'decreasing'
    
    # Tendencia de grasa corporal
    recent_bf = [e.body_fat_percentage for e in entries[:3] if e.body_fat_percentage is not None]
    bf_trend = 'stable'
    if len(recent_bf) >= 2:
        if recent_bf[0] > recent_bf[-1]:
            bf_trend = 'increasing'
        elif recent_bf[0] < recent_bf[-1]:
            bf_trend = 'decreasing'
    
    return {
        'weight_trend': weight_trend,
        'body_fat_trend': bf_trend
    }

def prepare_chart_data(entries):
    """Prepara datos para gráficos"""
    chart_data = {
        'weight': [],
        'body_fat': [],
        'dates': []
    }
    
    for entry in reversed(entries):  # Orden cronológico para gráficos
        chart_data['dates'].append(entry.date.isoformat())
        chart_data['weight'].append(entry.weight)
        chart_data['body_fat'].append(entry.body_fat_percentage)
    
    return chart_data

