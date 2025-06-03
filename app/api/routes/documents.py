import os
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from werkzeug.utils import secure_filename
import re

from app.models.document import Document
from app.models.recent_view import RecentView
from app.schemas.document import (
    DocumentSchema,
    DocumentUpdateSchema,
    DocumentSearchSchema
)
from app.core.security import document_access_required, log_activity
from app.core.config import Config

documents_bp = Blueprint('documents', __name__)

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@documents_bp.route('', methods=['POST'])
@jwt_required()
@log_activity('document_create')
def create_document():
    """Create a new document."""
    try:
        data = DocumentSchema().load(request.form)
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 422

    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), 400
    
    file = request.files['file']
    if not file or not allowed_file(file.filename):
        return jsonify({'message': 'Invalid file type'}), 400

    current_user_id = get_jwt_identity()
    
    # Create document
    document = Document(
        owner_id=current_user_id,
        file=file,
        **data
    )
    document.save()

    return jsonify({
        'message': 'Document created successfully',
        'document': DocumentSchema().dump(document)
    }), 201

@documents_bp.route('', methods=['GET'])
@jwt_required()
def list_documents():
    """List documents with pagination and search."""
    try:
        params = DocumentSearchSchema().load(request.args)
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 422

    current_user_id = get_jwt_identity()
    
    # Get paginated documents
    pagination = Document.search(
        query=params.get('query'),
        user_id=current_user_id,
        document_type=params.get('document_type'),
        page=params.get('page', 1),
        per_page=params.get('per_page', Config.DEFAULT_PAGE_SIZE)
    )

    return jsonify({
        'documents': DocumentSchema(many=True).dump(pagination.items),
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })

@documents_bp.route('/<int:document_id>', methods=['GET'])
@jwt_required()
@document_access_required
@log_activity('document_view')
def get_document(document_id):
    """Get a specific document."""
    document = Document.get_by_id(document_id)
    if not document:
        return jsonify({'message': 'Document not found'}), 404

    current_user_id = get_jwt_identity()
    
    # Record view
    RecentView.add_view(current_user_id, document_id)

    return jsonify(DocumentSchema().dump(document))

@documents_bp.route('/<int:document_id>', methods=['PUT'])
@jwt_required()
@document_access_required
@log_activity('document_update')
def update_document(document_id):
    """Update a document."""
    try:
        data = DocumentUpdateSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 422

    document = Document.get_by_id(document_id)
    if not document:
        return jsonify({'message': 'Document not found'}), 404

    # Update document
    document.update(**data)

    return jsonify({
        'message': 'Document updated successfully',
        'document': DocumentSchema().dump(document)
    })

@documents_bp.route('/<int:document_id>', methods=['DELETE'])
@jwt_required()
@document_access_required
@log_activity('document_delete')
def delete_document(document_id):
    """Delete a document."""
    document = Document.get_by_id(document_id)
    if not document:
        return jsonify({'message': 'Document not found'}), 404

    # Delete file
    try:
        os.remove(document.get_full_path())
    except OSError:
        current_app.logger.warning(f"Could not delete file for document {document_id}")

    # Delete document
    document.delete()

    return jsonify({'message': 'Document deleted successfully'})

@documents_bp.route('/<int:document_id>/download', methods=['GET'])
@jwt_required()
@document_access_required
@log_activity('document_download')
def download_document(document_id):
    """Download a document file."""
    document = Document.get_by_id(document_id)
    if not document:
        return jsonify({'message': 'Document not found'}), 404

    try:
        # Sanitize the original title
        safe_title = re.sub(r'[^\w\-\.]', '_', document.title)
        download_name = secure_filename(f"{safe_title}.{document.file_type}")
        
        return send_file(
            document.get_full_path(),
            mimetype=document.mime_type,
            as_attachment=True,
            download_name=download_name
        )
    except FileNotFoundError:
        return jsonify({'message': 'Document file not found'}), 404

@documents_bp.route('/recent', methods=['GET'])
@jwt_required()
def get_recent_documents():
    """Get user's recently viewed documents."""
    current_user_id = get_jwt_identity()
    recent_views = RecentView.get_user_recent_views(current_user_id)
    
    documents = [view.document for view in recent_views if view.document]
    
    return jsonify({
        'documents': DocumentSchema(many=True).dump(documents)
    }) 