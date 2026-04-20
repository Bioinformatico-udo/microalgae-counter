from flask import render_template, Blueprint

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/batch-setup')
def batch_setup():
    return render_template('batch_setup.html')

@main_bp.route('/batch-count/<int:batch_id>')
def batch_count(batch_id):
    return render_template('batch_count.html', batch_id=batch_id)

@main_bp.route('/batch-results/<int:batch_id>')
def batch_results(batch_id):
    return render_template('batch_results.html', batch_id=batch_id)

@main_bp.route('/upload')
def upload():
    return render_template('upload.html')

@main_bp.route('/manual-count')
def manual_count():
    return render_template('manual_count.html')

@main_bp.route('/results')
def results():
    return render_template('results.html')

@main_bp.route('/history')
def history():
    return render_template('history.html')