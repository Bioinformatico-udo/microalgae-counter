"""
API routes for handling counting operations and data management.
"""

from flask import request, jsonify, Blueprint, current_app
from models.yolo_counter import YOLOCounter
from models.model_manager import model_manager
from models.statistical_analysis import StatisticalAnalyzer
from app import db
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import time

api_bp = Blueprint('api', __name__)

analyzer = StatisticalAnalyzer()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


# Helper to get models
def get_models():
    from app import models
    return models


# ==================== BATCH MANAGEMENT ====================

@api_bp.route('/create-batch', methods=['POST'])
def create_batch():
    try:
        data = request.json
        batch_name = data.get('name')
        description = data.get('description', '')
        created_by = data.get('created_by', 'admin')
        image_ids = data.get('image_ids', [])
        culture_type = data.get('culture_type', 'monoclonal')
        
        if not batch_name:
            return jsonify({'error': 'Batch name is required'}), 400
        
        models = get_models()
        Batch = models['Batch']
        Image = models['Image']
        
        batch = Batch(
            name=batch_name,
            description=description,
            created_by=created_by,
            created_at=datetime.now(),
            total_images=len(image_ids),
            culture_type=culture_type,
            is_active=True
        )
        db.session.add(batch)
        db.session.flush()
        
        for image_id in image_ids:
            image = Image.query.get(image_id)
            if image:
                image.batch_id = batch.id
                image.culture_type = culture_type
        
        db.session.commit()
        
        return jsonify({'success': True, 'batch_id': batch.id, 'name': batch.name, 'total_images': batch.total_images})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/batches', methods=['GET'])
def get_batches():
    try:
        models = get_models()
        Batch = models['Batch']
        BatchCountingSession = models['BatchCountingSession']
        
        batches = Batch.query.order_by(Batch.created_at.desc()).all()
        result = []
        for batch in batches:
            sessions = BatchCountingSession.query.filter_by(batch_id=batch.id).all()
            technicians = [s.technician_name for s in sessions if s.is_completed]
            culture_type = getattr(batch, 'culture_type', 'monoclonal')
            result.append({
                'id': batch.id,
                'name': batch.name,
                'description': batch.description,
                'culture_type': culture_type,
                'created_at': batch.created_at.isoformat(),
                'created_by': batch.created_by,
                'total_images': batch.total_images,
                'technicians_completed': technicians,
                'is_active': batch.is_active
            })
        return jsonify({'success': True, 'batches': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/batch/<int:batch_id>/images', methods=['GET'])
def get_batch_images(batch_id):
    try:
        models = get_models()
        Batch = models['Batch']
        Image = models['Image']
        
        batch = Batch.query.get(batch_id)
        if not batch:
            return jsonify({'error': 'Batch not found'}), 404
        images = Image.query.filter_by(batch_id=batch_id).all()
        result = [{'id': img.id, 'filename': img.filename, 'original_filename': img.original_filename,
                   'url': f'/uploads/{img.filename}', 'order_index': idx, 'culture_type': img.culture_type}
                  for idx, img in enumerate(images)]
        return jsonify({'success': True, 'batch_id': batch_id, 'batch_name': batch.name,
                        'images': result, 'total_images': len(result)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== BATCH MANUAL COUNTING ====================

@api_bp.route('/batch/start-session', methods=['POST'])
def start_batch_session():
    try:
        models = get_models()
        BatchCountingSession = models['BatchCountingSession']
        
        data = request.json
        batch_id = data.get('batch_id')
        technician_name = data.get('technician_name')
        
        if not batch_id or not technician_name:
            return jsonify({'error': 'Batch ID and technician name required'}), 400
        
        existing = BatchCountingSession.query.filter_by(
            batch_id=batch_id, technician_name=technician_name, is_completed=False).first()
        if existing:
            return jsonify({'success': True, 'session_id': existing.id, 'message': 'Resuming existing session'})
        
        session = BatchCountingSession(
            batch_id=batch_id, technician_name=technician_name, start_time=datetime.now(), is_completed=False)
        db.session.add(session)
        db.session.commit()
        return jsonify({'success': True, 'session_id': session.id, 'message': 'Session started successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/batch/save-count', methods=['POST'])
def save_batch_image_count():
    try:
        models = get_models()
        BatchImageCount = models['BatchImageCount']
        
        data = request.json
        session_id = data.get('session_id')
        image_id = data.get('image_id')
        count = data.get('count')
        time_taken = data.get('time_taken')
        order_index = data.get('order_index', 0)
        notes = data.get('notes', '')
        culture_type = data.get('culture_type', 'monoclonal')
        
        species1 = data.get('species1')
        species2 = data.get('species2')
        species3 = data.get('species3')
        
        if not all([session_id, image_id, count is not None, time_taken is not None]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        existing = BatchImageCount.query.filter_by(session_id=session_id, image_id=image_id).first()
        if existing:
            existing.manual_count = count
            existing.time_taken_seconds = time_taken
            existing.notes = notes
            existing.timestamp = datetime.now()
            if culture_type == 'policlonal':
                existing.manual_count_species1 = species1
                existing.manual_count_species2 = species2
                existing.manual_count_species3 = species3
        else:
            image_count = BatchImageCount(
                session_id=session_id,
                image_id=image_id,
                manual_count=count,
                time_taken_seconds=time_taken,
                order_index=order_index,
                notes=notes,
                timestamp=datetime.now()
            )
            if culture_type == 'policlonal':
                image_count.manual_count_species1 = species1
                image_count.manual_count_species2 = species2
                image_count.manual_count_species3 = species3
            db.session.add(image_count)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Count saved successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/batch/end-session', methods=['POST'])
def end_batch_session():
    try:
        models = get_models()
        BatchCountingSession = models['BatchCountingSession']
        BatchImageCount = models['BatchImageCount']
        
        data = request.json
        session_id = data.get('session_id')
        session = BatchCountingSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        counts = BatchImageCount.query.filter_by(session_id=session_id).all()
        total_time = sum(c.time_taken_seconds for c in counts)
        session.end_time = datetime.now()
        session.total_time_seconds = total_time
        session.is_completed = True
        db.session.commit()
        return jsonify({'success': True, 'total_time': total_time, 'total_images': len(counts), 'message': 'Session completed'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/batch/session-status/<int:session_id>', methods=['GET'])
def get_batch_session_status(session_id):
    try:
        models = get_models()
        BatchCountingSession = models['BatchCountingSession']
        Batch = models['Batch']
        BatchImageCount = models['BatchImageCount']
        Image = models['Image']
        
        session = BatchCountingSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        batch = Batch.query.get(session.batch_id)
        total_images = batch.total_images if batch else 0
        counts = BatchImageCount.query.filter_by(session_id=session_id).all()
        completed_images = len(counts)
        completed_image_ids = [c.image_id for c in counts]
        remaining_images = Image.query.filter(
            Image.batch_id == session.batch_id,
            Image.id.notin_(completed_image_ids) if completed_image_ids else True
        ).all()
        
        return jsonify({
            'success': True, 
            'session_id': session.id, 
            'technician_name': session.technician_name,
            'start_time': session.start_time.isoformat(), 
            'is_completed': session.is_completed,
            'completed_images': completed_images, 
            'total_images': total_images,
            'remaining_images': [{'id': img.id, 'filename': img.filename, 'original_filename': img.original_filename} for idx, img in enumerate(remaining_images)],
            'counts': [{'image_id': c.image_id, 'count': c.manual_count, 'time_taken': c.time_taken_seconds} for c in counts]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== BATCH AUTOMATIC COUNTING ====================

@api_bp.route('/batch/auto-count/<int:batch_id>', methods=['POST'])
def batch_automatic_count(batch_id):
    try:
        models = get_models()
        Batch = models['Batch']
        Image = models['Image']
        AutomaticBatchResult = models['AutomaticBatchResult']
        AutomaticImageResult = models['AutomaticImageResult']
        
        data = request.json or {}
        model_type = data.get('model_type', 'default')
        model_name = data.get('model_name', None)
        
        batch = Batch.query.get(batch_id)
        if not batch:
            return jsonify({'error': 'Batch not found'}), 404
        
        images = Image.query.filter_by(batch_id=batch_id).all()
        if not images:
            return jsonify({'error': 'No images in batch'}), 400
        
        if model_name:
            model_manager.set_model(model_name)
        elif model_type != 'default':
            models_list = model_manager.get_models_by_type(model_type)
            if models_list:
                model_manager.set_model(models_list[0].name)
        
        batch_result = AutomaticBatchResult(
            batch_id=batch_id, 
            model_used=model_manager.current_model or 'demonstration',
            model_type=model_type, 
            processed_at=datetime.now()
        )
        db.session.add(batch_result)
        db.session.flush()
        
        results = []
        total_time = 0
        
        for idx, image in enumerate(images):
            start_time = time.time()
            count_result = model_manager.count_microalgae(image.filepath, model_type if model_type != 'default' else None)
            processing_time = time.time() - start_time
            total_time += processing_time
            
            image_result = AutomaticImageResult(
                batch_result_id=batch_result.id, 
                image_id=image.id, 
                count=count_result['count'],
                processing_time=processing_time, 
                order_index=idx, 
                confidence=count_result.get('avg_confidence'),
                detection_details=count_result.get('detections', [])
            )
            db.session.add(image_result)
            results.append({
                'image_id': image.id, 
                'filename': image.original_filename, 
                'count': count_result['count'],
                'processing_time': processing_time, 
                'model_used': count_result.get('model_used', 'demonstration')
            })
        
        batch_result.total_time_seconds = total_time
        batch_result.results = results
        db.session.commit()
        
        # Calcular el promedio de tiempo por imagen (VERIFICADO Y CORRECTO)
        num_images = len(images)
        if num_images > 0:
            average_time_per_image = total_time / num_images
        else:
            average_time_per_image = 0
        
        return jsonify({
            'success': True, 
            'batch_id': batch_id, 
            'batch_name': batch.name,
            'model_used': model_manager.current_model or 'demonstration', 
            'model_type': model_type,
            'total_time': total_time, 
            'average_time_per_image': average_time_per_image,
            'total_images': num_images, 
            'results': results
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error in batch_automatic_count: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/batch/auto-results/<int:batch_id>', methods=['GET'])
def get_batch_auto_results(batch_id):
    try:
        models = get_models()
        AutomaticBatchResult = models['AutomaticBatchResult']
        BatchCountingSession = models['BatchCountingSession']
        BatchImageCount = models['BatchImageCount']
        Batch = models['Batch']
        
        batch_result = AutomaticBatchResult.query.filter_by(batch_id=batch_id)\
            .order_by(AutomaticBatchResult.processed_at.desc()).first()
        if not batch_result:
            return jsonify({'success': True, 'has_results': False, 'message': 'No automatic counting performed yet'})
        
        sessions = BatchCountingSession.query.filter_by(batch_id=batch_id, is_completed=True).all()
        manual_results_by_technician = {}
        for session in sessions:
            counts = BatchImageCount.query.filter_by(session_id=session.id).all()
            manual_counts_dict = {}
            for c in counts:
                if hasattr(c, 'manual_count_species1') and c.manual_count_species1 is not None:
                    manual_counts_dict[c.image_id] = {
                        'total': c.manual_count,
                        'species1': c.manual_count_species1,
                        'species2': c.manual_count_species2,
                        'species3': c.manual_count_species3
                    }
                else:
                    manual_counts_dict[c.image_id] = c.manual_count
            manual_results_by_technician[session.technician_name] = {
                'total_time': session.total_time_seconds,
                'counts': manual_counts_dict,
                'completed_at': session.end_time.isoformat() if session.end_time else None
            }
        
        auto_counts = {}
        for img_result in batch_result.image_results:
            auto_counts[img_result.image_id] = {
                'count': img_result.count,
                'processing_time': img_result.processing_time
            }
        
        return jsonify({'success': True, 'has_results': True, 'batch_id': batch_id,
                       'batch_name': Batch.query.get(batch_id).name,
                       'model_used': batch_result.model_used, 'model_type': batch_result.model_type,
                       'processed_at': batch_result.processed_at.isoformat(), 
                       'total_time_auto': batch_result.total_time_seconds,
                       'manual_results': manual_results_by_technician, 
                       'auto_counts': auto_counts,
                       'detailed_results': batch_result.results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== BATCH CORRELATION ANALYSIS ====================

@api_bp.route('/batch/analyze-correlation/<int:batch_id>', methods=['GET'])
def analyze_batch_correlation(batch_id):
    try:
        models = get_models()
        AutomaticBatchResult = models['AutomaticBatchResult']
        BatchCountingSession = models['BatchCountingSession']
        BatchImageCount = models['BatchImageCount']
        Image = models['Image']
        
        batch_result = AutomaticBatchResult.query.filter_by(batch_id=batch_id)\
            .order_by(AutomaticBatchResult.processed_at.desc()).first()
        if not batch_result:
            return jsonify({'error': 'No automatic results found for this batch'}), 400
        
        sessions = BatchCountingSession.query.filter_by(batch_id=batch_id, is_completed=True).all()
        if not sessions:
            return jsonify({'error': 'No manual counting sessions completed for this batch'}), 400
        
        all_manual_counts = []
        all_auto_counts = []
        technician_results = []
        
        images = Image.query.filter_by(batch_id=batch_id).all()
        auto_counts_dict = {img_result.image_id: img_result.count for img_result in batch_result.image_results}
        
        for session in sessions:
            counts = BatchImageCount.query.filter_by(session_id=session.id).all()
            manual_dict = {}
            for c in counts:
                if hasattr(c, 'manual_count_species1') and c.manual_count_species1 is not None:
                    manual_dict[c.image_id] = c.manual_count
                else:
                    manual_dict[c.image_id] = c.manual_count
            manual_vals = []
            auto_vals = []
            for image_id in manual_dict:
                if image_id in auto_counts_dict:
                    manual_vals.append(manual_dict[image_id])
                    auto_vals.append(auto_counts_dict[image_id])
                    all_manual_counts.append(manual_dict[image_id])
                    all_auto_counts.append(auto_counts_dict[image_id])
            
            if len(manual_vals) >= 2:
                corr_result = analyzer.pearson_correlation(manual_vals, auto_vals)
                technician_results.append({
                    'technician': session.technician_name,
                    'correlation': corr_result['correlation'],
                    'p_value': corr_result['p_value'],
                    'interpretation': corr_result['interpretation'],
                    'n_samples': len(manual_vals), 
                    'total_time': session.total_time_seconds
                })
        
        global_correlation = None
        if len(all_manual_counts) >= 2:
            global_correlation = analyzer.pearson_correlation(all_manual_counts, all_auto_counts)
        
        plot_url = None
        if len(all_manual_counts) >= 2:
            plot_path = f'static/images/correlation_batch_{batch_id}.png'
            os.makedirs('static/images', exist_ok=True)
            analyzer.create_correlation_plot(all_manual_counts, all_auto_counts, plot_path)
            plot_url = f'/static/images/correlation_batch_{batch_id}.png'
        
        return jsonify({
            'success': True, 
            'batch_id': batch_id, 
            'global_correlation': global_correlation,
            'technician_results': technician_results, 
            'plot_url': plot_url, 
            'total_images': len(images),
            'total_technicians': len(sessions), 
            'auto_model': batch_result.model_used,
            'auto_processed_at': batch_result.processed_at.isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== IMAGE UPLOAD ====================

@api_bp.route('/upload-image', methods=['POST'])
def upload_image():
    try:
        models = get_models()
        Image = models['Image']
        
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        culture_type = request.form.get('culture_type', 'monoclonal')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            image = Image(
                filename=unique_filename, 
                original_filename=filename, 
                filepath=filepath,
                upload_date=datetime.now(), 
                culture_type=culture_type
            )
            db.session.add(image)
            db.session.commit()
            
            return jsonify({'success': True, 'image_id': image.id, 'filename': unique_filename, 'culture_type': culture_type})
        
        return jsonify({'error': 'File type not allowed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/upload-multiple', methods=['POST'])
def upload_multiple_images():
    try:
        models = get_models()
        Image = models['Image']
        
        if 'images' not in request.files:
            return jsonify({'error': 'No image files provided'}), 400
        
        files = request.files.getlist('images')
        culture_type = request.form.get('culture_type', 'monoclonal')
        uploaded_images = []
        
        for file in files:
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"{timestamp}_{filename}"
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(filepath)
                
                image = Image(
                    filename=unique_filename, 
                    original_filename=filename, 
                    filepath=filepath,
                    upload_date=datetime.now(), 
                    culture_type=culture_type
                )
                db.session.add(image)
                db.session.flush()
                uploaded_images.append({'id': image.id, 'filename': filename, 'url': f'/uploads/{unique_filename}'})
        
        db.session.commit()
        return jsonify({'success': True, 'uploaded_count': len(uploaded_images), 'images': uploaded_images})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== LEGACY ENDPOINTS ====================

@api_bp.route('/manual-count', methods=['POST'])
def save_manual_count():
    try:
        models = get_models()
        CountSession = models['CountSession']
        ManualCount = models['ManualCount']
        
        data = request.json
        technician_name = data.get('technician_name')
        image_id = data.get('image_id')
        count_value = data.get('count')
        time_taken = data.get('time_taken')
        notes = data.get('notes', '')
        culture_type = data.get('culture_type', 'monoclonal')
        
        if not all([technician_name, image_id, count_value is not None]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        session = CountSession.query.filter_by(technician_name=technician_name, is_active=True).first()
        if not session:
            session = CountSession(
                technician_name=technician_name, 
                start_time=datetime.now(), 
                is_active=True, 
                culture_type=culture_type
            )
            db.session.add(session)
            db.session.commit()
        
        manual_count = ManualCount(
            session_id=session.id, 
            image_id=image_id, 
            count=count_value,
            time_taken_seconds=time_taken or 0, 
            timestamp=datetime.now(), 
            notes=notes, 
            culture_type=culture_type
        )
        db.session.add(manual_count)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Manual count saved successfully', 'count_id': manual_count.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/auto-count/<int:image_id>', methods=['GET'])
def automatic_count(image_id):
    try:
        models = get_models()
        Image = models['Image']
        AutomaticCount = models['AutomaticCount']
        
        image = Image.query.get(image_id)
        if not image:
            return jsonify({'error': 'Image not found'}), 404
        
        model_type = request.args.get('model_type', 'default')
        model_name = request.args.get('model_name', None)
        
        if model_name:
            model_manager.set_model(model_name)
        elif model_type != 'default':
            models_list = model_manager.get_models_by_type(model_type)
            if models_list:
                model_manager.set_model(models_list[0].name)
        
        result = model_manager.count_microalgae(image.filepath, model_type if model_type != 'default' else None)
        
        auto_count = AutomaticCount(
            image_id=image_id, 
            count=result['count'], 
            processing_time=result['processing_time'],
            model_version=result.get('model_used', 'unknown'), 
            model_type=result.get('model_type', 'unknown'),
            timestamp=datetime.now(), 
            detection_details=result.get('detections', [])
        )
        db.session.add(auto_count)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'count': result['count'], 
            'processing_time': result['processing_time'],
            'detections': result.get('detections', []), 
            'model_used': result.get('model_used', 'demonstration'),
            'model_type': result.get('model_type', 'demonstration')
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/models', methods=['GET'])
def get_available_models():
    try:
        all_models = model_manager.get_all_models()
        current_model = model_manager.get_current_model()
        models_by_type = {'default': [], 'monoclonal': [], 'policlonal': [], 'refined': []}
        
        for name, info in all_models.items():
            models_by_type[info.model_type].append({
                'name': name, 
                'version': info.version, 
                'accuracy': info.accuracy,
                'training_date': info.training_date, 
                'description': info.description,
                'is_active': name == current_model.name if current_model else False
            })
        
        return jsonify({
            'success': True, 
            'models': models_by_type,
            'current_model': {
                'name': current_model.name if current_model else None,
                'type': current_model.model_type if current_model else None,
                'version': current_model.version if current_model else None
            } if current_model else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/select-model', methods=['POST'])
def select_model():
    try:
        data = request.json
        model_name = data.get('model_name')
        model_type = data.get('model_type')
        
        if model_name:
            success = model_manager.set_model(model_name)
        elif model_type:
            models_list = model_manager.get_models_by_type(model_type)
            if models_list:
                success = model_manager.set_model(models_list[0].name)
            else:
                return jsonify({'error': f'No {model_type} models found'}), 404
        else:
            return jsonify({'error': 'Must provide model_name or model_type'}), 400
        
        if success:
            current = model_manager.get_current_model()
            return jsonify({
                'success': True, 
                'message': f'Model selected: {current.name}',
                'current_model': {
                    'name': current.name, 
                    'type': current.model_type, 
                    'version': current.version
                }
            })
        else:
            return jsonify({'error': 'Failed to select model'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/technician-history/<technician_name>', methods=['GET'])
def get_technician_history(technician_name):
    try:
        models = get_models()
        CountSession = models['CountSession']
        ManualCount = models['ManualCount']
        
        sessions = CountSession.query.filter_by(technician_name=technician_name).all()
        history = []
        for session in sessions:
            counts = ManualCount.query.filter_by(session_id=session.id).all()
            history.append({
                'session_id': session.id, 
                'technician': session.technician_name,
                'start_time': session.start_time.isoformat(),
                'end_time': session.end_time.isoformat() if session.end_time else None,
                'total_images': len(counts),
                'counts': [{
                    'count_id': c.id, 
                    'image_id': c.image_id, 
                    'count': c.count,
                    'time_taken': c.time_taken_seconds, 
                    'timestamp': c.timestamp.isoformat(),
                    'culture_type': c.culture_type
                } for c in counts]
            })
        return jsonify({'success': True, 'technician': technician_name, 'history': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/all-history', methods=['GET'])
def get_all_history():
    try:
        models = get_models()
        CountSession = models['CountSession']
        ManualCount = models['ManualCount']
        
        sessions = CountSession.query.order_by(CountSession.start_time.desc()).all()
        history = []
        for session in sessions:
            counts = ManualCount.query.filter_by(session_id=session.id).all()
            if counts:
                history.append({
                    'session_id': session.id, 
                    'technician': session.technician_name,
                    'start_time': session.start_time.isoformat(),
                    'end_time': session.end_time.isoformat() if session.end_time else None,
                    'total_images': len(counts),
                    'counts': [{
                        'count_id': c.id, 
                        'image_id': c.image_id, 
                        'count': c.count,
                        'time_taken': c.time_taken_seconds, 
                        'timestamp': c.timestamp.isoformat(),
                        'culture_type': c.culture_type
                    } for c in counts]
                })
        return jsonify({'success': True, 'history': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/end-session', methods=['POST'])
def end_session():
    try:
        models = get_models()
        CountSession = models['CountSession']
        
        data = request.json
        technician_name = data.get('technician_name')
        session = CountSession.query.filter_by(technician_name=technician_name, is_active=True).first()
        if session:
            session.end_time = datetime.now()
            session.is_active = False
            db.session.commit()
            return jsonify({'success': True, 'message': 'Session ended'})
        return jsonify({'success': False, 'message': 'No active session found'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500