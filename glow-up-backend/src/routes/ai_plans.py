from flask import Blueprint, jsonify, request
from src.models.user import User, WorkoutPlan, NutritionPlan, PlanFeedback, db
from src.routes.auth import token_required
import json
import openai
import os
from datetime import datetime, timedelta

ai_plans_bp = Blueprint('ai_plans', __name__)

# Configurar OpenAI (se configurará cuando se proporcione la API key)
openai.api_key = os.environ.get('OPENAI_API_KEY')

@ai_plans_bp.route('/generate-workout-plan', methods=['POST'])
@token_required
def generate_workout_plan(current_user):
    try:
        data = request.json
        duration_weeks = data.get('duration_weeks', 4)
        
        # Obtener feedback previo para personalización
        previous_feedback = PlanFeedback.query.filter_by(
            user_id=current_user.id,
            plan_type='workout'
        ).order_by(PlanFeedback.created_at.desc()).limit(5).all()
        
        # Construir prompt para OpenAI
        prompt = build_workout_prompt(current_user, duration_weeks, previous_feedback)
        
        # Generar plan con OpenAI (simulado por ahora)
        if openai.api_key:
            plan_data = generate_with_openai(prompt, 'workout')
        else:
            plan_data = generate_mock_workout_plan(current_user, duration_weeks)
        
        # Guardar plan en la base de datos
        workout_plan = WorkoutPlan(
            user_id=current_user.id,
            title=f"Plan de Entrenamiento - {duration_weeks} semanas",
            description=f"Plan personalizado para {current_user.goal}",
            duration_weeks=duration_weeks,
            difficulty_level=current_user.experience_level,
            plan_data=json.dumps(plan_data),
            ai_generated=True,
            is_active=True
        )
        
        # Desactivar planes anteriores
        WorkoutPlan.query.filter_by(user_id=current_user.id, is_active=True).update({'is_active': False})
        
        db.session.add(workout_plan)
        db.session.commit()
        
        return jsonify({
            'message': 'Plan de entrenamiento generado exitosamente',
            'plan': workout_plan.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_plans_bp.route('/generate-nutrition-plan', methods=['POST'])
@token_required
def generate_nutrition_plan(current_user):
    try:
        data = request.json
        duration_weeks = data.get('duration_weeks', 4)
        
        # Obtener feedback previo para personalización
        previous_feedback = PlanFeedback.query.filter_by(
            user_id=current_user.id,
            plan_type='nutrition'
        ).order_by(PlanFeedback.created_at.desc()).limit(5).all()
        
        # Construir prompt para OpenAI
        prompt = build_nutrition_prompt(current_user, duration_weeks, previous_feedback)
        
        # Generar plan con OpenAI (simulado por ahora)
        if openai.api_key:
            plan_data = generate_with_openai(prompt, 'nutrition')
        else:
            plan_data = generate_mock_nutrition_plan(current_user, duration_weeks)
        
        # Calcular calorías diarias basadas en el objetivo del usuario
        daily_calories = calculate_daily_calories(current_user)
        
        # Guardar plan en la base de datos
        nutrition_plan = NutritionPlan(
            user_id=current_user.id,
            title=f"Plan Nutricional - {duration_weeks} semanas",
            description=f"Plan personalizado para {current_user.goal}",
            duration_weeks=duration_weeks,
            daily_calories=daily_calories,
            macros=json.dumps(plan_data['macros']),
            meal_plan=json.dumps(plan_data['meal_plan']),
            ai_generated=True,
            is_active=True
        )
        
        # Desactivar planes anteriores
        NutritionPlan.query.filter_by(user_id=current_user.id, is_active=True).update({'is_active': False})
        
        db.session.add(nutrition_plan)
        db.session.commit()
        
        return jsonify({
            'message': 'Plan nutricional generado exitosamente',
            'plan': nutrition_plan.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_plans_bp.route('/submit-feedback', methods=['POST'])
@token_required
def submit_feedback(current_user):
    try:
        data = request.json
        
        feedback = PlanFeedback(
            user_id=current_user.id,
            plan_type=data['plan_type'],
            plan_id=data['plan_id'],
            rating=data['rating'],
            feedback_text=data.get('feedback_text'),
            difficulty_rating=data.get('difficulty_rating'),
            satisfaction_rating=data.get('satisfaction_rating')
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        return jsonify({
            'message': 'Feedback enviado exitosamente',
            'feedback': feedback.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_plans_bp.route('/my-plans', methods=['GET'])
@token_required
def get_my_plans(current_user):
    try:
        workout_plans = WorkoutPlan.query.filter_by(user_id=current_user.id).order_by(WorkoutPlan.created_at.desc()).all()
        nutrition_plans = NutritionPlan.query.filter_by(user_id=current_user.id).order_by(NutritionPlan.created_at.desc()).all()
        
        return jsonify({
            'workout_plans': [plan.to_dict() for plan in workout_plans],
            'nutrition_plans': [plan.to_dict() for plan in nutrition_plans]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def build_workout_prompt(user, duration_weeks, previous_feedback):
    """Construye el prompt para generar un plan de entrenamiento"""
    feedback_text = ""
    if previous_feedback:
        feedback_text = "Feedback de planes anteriores:\n"
        for feedback in previous_feedback:
            feedback_text += f"- Rating: {feedback.rating}/5, Dificultad: {feedback.difficulty_rating}/5, Comentario: {feedback.feedback_text}\n"
    
    equipment_available = user.equipment_available if user.equipment_available else "Equipo básico de gimnasio"
    
    prompt = f"""
    Genera un plan de entrenamiento personalizado para un usuario con las siguientes características:
    
    Información del usuario:
    - Edad: {user.age} años
    - Peso: {user.weight} kg
    - Altura: {user.height} cm
    - Objetivo: {user.goal}
    - Nivel de experiencia: {user.experience_level}
    - Nivel de actividad: {user.activity_level}
    - Equipo disponible: {equipment_available}
    
    Duración del plan: {duration_weeks} semanas
    
    {feedback_text}
    
    Genera un plan estructurado con:
    1. Cronograma semanal (7 días)
    2. Para cada día de entrenamiento: tipo de entrenamiento, grupos musculares, ejercicios específicos
    3. Para cada ejercicio: series, repeticiones, peso sugerido (si aplica), tempo (para usuarios avanzados)
    4. Días de descanso y cardio
    5. Progresión semanal
    
    Responde en formato JSON con la estructura especificada.
    """
    return prompt

def build_nutrition_prompt(user, duration_weeks, previous_feedback):
    """Construye el prompt para generar un plan nutricional"""
    feedback_text = ""
    if previous_feedback:
        feedback_text = "Feedback de planes anteriores:\n"
        for feedback in previous_feedback:
            feedback_text += f"- Rating: {feedback.rating}/5, Comentario: {feedback.feedback_text}\n"
    
    daily_calories = calculate_daily_calories(user)
    dietary_restrictions = user.dietary_restrictions if user.dietary_restrictions else "Ninguna"
    
    prompt = f"""
    Genera un plan nutricional personalizado para un usuario con las siguientes características:
    
    Información del usuario:
    - Edad: {user.age} años
    - Peso: {user.weight} kg
    - Altura: {user.height} cm
    - Objetivo: {user.goal}
    - Nivel de actividad: {user.activity_level}
    - Restricciones dietéticas: {dietary_restrictions}
    - Calorías diarias objetivo: {daily_calories}
    
    Duración del plan: {duration_weeks} semanas
    
    {feedback_text}
    
    Genera un plan estructurado con:
    1. Distribución de macronutrientes
    2. Plan de comidas semanal con 2 opciones por comida
    3. Recetas detalladas con ingredientes y preparación
    4. Información nutricional por comida
    
    Responde en formato JSON con la estructura especificada.
    """
    return prompt

def generate_with_openai(prompt, plan_type):
    """Genera plan usando OpenAI API"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un experto en fitness y nutrición. Genera planes detallados y seguros."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000,
            temperature=0.7
        )
        
        plan_text = response.choices[0].message.content
        return json.loads(plan_text)
        
    except Exception as e:
        # Fallback a plan mock si OpenAI falla
        if plan_type == 'workout':
            return generate_mock_workout_plan(None, 4)
        else:
            return generate_mock_nutrition_plan(None, 4)

def generate_mock_workout_plan(user, duration_weeks):
    """Genera un plan de entrenamiento mock para pruebas"""
    return {
        "weekly_schedule": [
            {
                "day": "Lunes",
                "type": "Fuerza A",
                "muscle_groups": ["Pecho", "Tríceps", "Hombros"],
                "duration_minutes": 55,
                "exercises": [
                    {
                        "name": "Press de banca",
                        "sets": 4,
                        "reps": "8-10",
                        "weight_suggestion": "70% 1RM",
                        "tempo": "2-1-2-1",
                        "rest_seconds": 90
                    },
                    {
                        "name": "Press militar",
                        "sets": 3,
                        "reps": "10-12",
                        "weight_suggestion": "60% 1RM",
                        "tempo": "2-0-2-0",
                        "rest_seconds": 75
                    }
                ]
            },
            {
                "day": "Martes",
                "type": "Cardio",
                "muscle_groups": ["Cardiovascular"],
                "duration_minutes": 30,
                "exercises": [
                    {
                        "name": "Caminata rápida",
                        "sets": 1,
                        "reps": "30 minutos",
                        "intensity": "Moderada",
                        "heart_rate_zone": "60-70%"
                    }
                ]
            },
            {
                "day": "Miércoles",
                "type": "Fuerza B",
                "muscle_groups": ["Espalda", "Bíceps"],
                "duration_minutes": 55,
                "exercises": [
                    {
                        "name": "Dominadas",
                        "sets": 4,
                        "reps": "6-8",
                        "weight_suggestion": "Peso corporal",
                        "tempo": "2-1-2-1",
                        "rest_seconds": 120
                    }
                ]
            },
            {
                "day": "Jueves",
                "type": "Cardio",
                "muscle_groups": ["Cardiovascular"],
                "duration_minutes": 25,
                "exercises": []
            },
            {
                "day": "Viernes",
                "type": "Fuerza C",
                "muscle_groups": ["Piernas", "Glúteos"],
                "duration_minutes": 60,
                "exercises": [
                    {
                        "name": "Sentadillas",
                        "sets": 4,
                        "reps": "10-12",
                        "weight_suggestion": "80% 1RM",
                        "tempo": "3-1-1-1",
                        "rest_seconds": 120
                    }
                ]
            },
            {
                "day": "Sábado",
                "type": "Cardio",
                "muscle_groups": ["Cardiovascular"],
                "duration_minutes": 40,
                "exercises": []
            },
            {
                "day": "Domingo",
                "type": "Descanso",
                "muscle_groups": [],
                "duration_minutes": 0,
                "exercises": []
            }
        ],
        "progression": {
            "week_1": "Adaptación - Enfoque en técnica",
            "week_2": "Incremento de volumen - +10% repeticiones",
            "week_3": "Intensidad máxima - +5% peso",
            "week_4": "Deload - -20% volumen para recuperación"
        }
    }

def generate_mock_nutrition_plan(user, duration_weeks):
    """Genera un plan nutricional mock para pruebas"""
    return {
        "macros": {
            "protein_grams": 150,
            "carbs_grams": 200,
            "fat_grams": 80,
            "protein_percentage": 30,
            "carbs_percentage": 40,
            "fat_percentage": 30
        },
        "meal_plan": {
            "week_1": {
                "monday": {
                    "breakfast": {
                        "option_1": {
                            "name": "Avena con frutas y proteína",
                            "ingredients": ["100g avena", "1 plátano", "200ml leche descremada", "1 scoop proteína"],
                            "preparation": "Cocinar la avena con leche, agregar plátano cortado y proteína en polvo",
                            "calories": 450,
                            "protein": 35,
                            "carbs": 55,
                            "fat": 8
                        },
                        "option_2": {
                            "name": "Huevos revueltos con tostadas",
                            "ingredients": ["3 huevos", "2 rebanadas pan integral", "1 aguacate", "tomate"],
                            "preparation": "Revolver huevos, tostar pan, agregar aguacate y tomate",
                            "calories": 480,
                            "protein": 25,
                            "carbs": 35,
                            "fat": 25
                        }
                    },
                    "lunch": {
                        "option_1": {
                            "name": "Pollo con arroz y verduras",
                            "ingredients": ["150g pechuga de pollo", "100g arroz integral", "verduras mixtas"],
                            "preparation": "Cocinar pollo a la plancha, hervir arroz, saltear verduras",
                            "calories": 520,
                            "protein": 45,
                            "carbs": 50,
                            "fat": 12
                        },
                        "option_2": {
                            "name": "Salmón con quinoa",
                            "ingredients": ["120g salmón", "80g quinoa", "espárragos", "limón"],
                            "preparation": "Hornear salmón con limón, cocinar quinoa, vapor espárragos",
                            "calories": 540,
                            "protein": 40,
                            "carbs": 45,
                            "fat": 18
                        }
                    },
                    "dinner": {
                        "option_1": {
                            "name": "Ensalada de atún",
                            "ingredients": ["150g atún en agua", "lechuga", "tomate", "pepino", "aceite oliva"],
                            "preparation": "Mezclar todos los ingredientes, aliñar con aceite de oliva",
                            "calories": 320,
                            "protein": 35,
                            "carbs": 15,
                            "fat": 15
                        },
                        "option_2": {
                            "name": "Pavo con vegetales",
                            "ingredients": ["120g pavo", "brócoli", "calabacín", "pimiento"],
                            "preparation": "Cocinar pavo a la plancha, saltear vegetales",
                            "calories": 300,
                            "protein": 32,
                            "carbs": 18,
                            "fat": 10
                        }
                    }
                }
            }
        }
    }

def calculate_daily_calories(user):
    """Calcula las calorías diarias basadas en el perfil del usuario"""
    # Fórmula de Harris-Benedict revisada
    if user.goal == 'lose_weight':
        bmr = 88.362 + (13.397 * user.weight) + (4.799 * user.height) - (5.677 * user.age)
    elif user.goal == 'gain_muscle':
        bmr = 88.362 + (13.397 * user.weight) + (4.799 * user.height) - (5.677 * user.age)
    else:  # maintain
        bmr = 88.362 + (13.397 * user.weight) + (4.799 * user.height) - (5.677 * user.age)
    
    # Factor de actividad
    activity_factors = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very_active': 1.9
    }
    
    activity_factor = activity_factors.get(user.activity_level, 1.55)
    tdee = bmr * activity_factor
    
    # Ajustar según objetivo
    if user.goal == 'lose_weight':
        return int(tdee - 500)  # Déficit de 500 calorías
    elif user.goal == 'gain_muscle':
        return int(tdee + 300)  # Superávit de 300 calorías
    else:
        return int(tdee)  # Mantenimiento

