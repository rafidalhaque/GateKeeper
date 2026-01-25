"""
SMTP Configuration routes
"""
from flask import Blueprint, request, jsonify
from app.models import db
from app.models.auth import SMTPConfig
from app.utils.auth import super_admin_required, get_current_user

bp = Blueprint('smtp', __name__, url_prefix='/api/smtp')


@bp.route('/config', methods=['GET'])
@super_admin_required
def get_smtp_config():
    """Get current SMTP configuration (super admin only)"""
    config = SMTPConfig.query.filter_by(is_active=True).first()

    if not config:
        return jsonify({
            'exists': False,
            'message': 'No SMTP configuration found. Using .env defaults.'
        })

    return jsonify({
        'exists': True,
        'config': {
            'id': config.id,
            'smtp_server': config.smtp_server,
            'smtp_port': config.smtp_port,
            'smtp_username': config.smtp_username,
            'smtp_password': '***HIDDEN***',  # Never expose password
            'smtp_use_tls': config.smtp_use_tls,
            'smtp_use_ssl': config.smtp_use_ssl,
            'sender_email': config.sender_email,
            'sender_name': config.sender_name,
            'is_active': config.is_active,
            'updated_at': config.updated_at.isoformat() if config.updated_at else None
        }
    })


@bp.route('/config', methods=['POST'])
@super_admin_required
def create_or_update_smtp_config():
    """Create or update SMTP configuration (super admin only)"""
    data = request.get_json()
    current_user = get_current_user()

    # Validate required fields
    required_fields = ['smtp_server', 'smtp_port', 'smtp_username', 'smtp_password', 'sender_email']
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

    # Deactivate any existing configs
    SMTPConfig.query.update({'is_active': False})

    # Create new config
    config = SMTPConfig(
        smtp_server=data['smtp_server'],
        smtp_port=data['smtp_port'],
        smtp_username=data['smtp_username'],
        smtp_password=data['smtp_password'],  # TODO: Encrypt in production
        smtp_use_tls=data.get('smtp_use_tls', True),
        smtp_use_ssl=data.get('smtp_use_ssl', False),
        sender_email=data['sender_email'],
        sender_name=data.get('sender_name', 'GateKeeper'),
        is_active=True,
        created_by=current_user.id
    )

    db.session.add(config)
    db.session.commit()

    return jsonify({
        'message': 'SMTP configuration saved successfully',
        'config': {
            'id': config.id,
            'smtp_server': config.smtp_server,
            'smtp_port': config.smtp_port,
            'sender_email': config.sender_email,
            'is_active': config.is_active
        }
    }), 201


@bp.route('/config/test', methods=['POST'])
@super_admin_required
def test_smtp_config():
    """Test SMTP configuration by sending a test email"""
    data = request.get_json()
    test_email = data.get('test_email')

    if not test_email:
        return jsonify({'error': 'Missing test_email'}), 400

    # Get active config or use provided config for testing
    config = SMTPConfig.query.filter_by(is_active=True).first()

    if not config and 'smtp_server' not in data:
        return jsonify({'error': 'No SMTP configuration found'}), 400

    # Use provided config for testing if available
    test_config = {
        'smtp_server': data.get('smtp_server', config.smtp_server if config else None),
        'smtp_port': data.get('smtp_port', config.smtp_port if config else 587),
        'smtp_username': data.get('smtp_username', config.smtp_username if config else None),
        'smtp_password': data.get('smtp_password', config.smtp_password if config else None),
        'smtp_use_tls': data.get('smtp_use_tls', config.smtp_use_tls if config else True),
        'smtp_use_ssl': data.get('smtp_use_ssl', config.smtp_use_ssl if config else False),
        'sender_email': data.get('sender_email', config.sender_email if config else None),
        'sender_name': data.get('sender_name', config.sender_name if config else 'GateKeeper')
    }

    # Send test email
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        message = MIMEMultipart('alternative')
        message['Subject'] = 'GateKeeper SMTP Test'
        message['From'] = f"{test_config['sender_name']} <{test_config['sender_email']}>"
        message['To'] = test_email

        text = "This is a test email from GateKeeper to verify SMTP configuration."
        html = f"""
        <html>
            <body>
                <h2>GateKeeper SMTP Test</h2>
                <p>This is a test email to verify your SMTP configuration.</p>
                <p><strong>Configuration:</strong></p>
                <ul>
                    <li>Server: {test_config['smtp_server']}:{test_config['smtp_port']}</li>
                    <li>TLS: {'Enabled' if test_config['smtp_use_tls'] else 'Disabled'}</li>
                    <li>SSL: {'Enabled' if test_config['smtp_use_ssl'] else 'Disabled'}</li>
                </ul>
                <p>If you received this email, your SMTP configuration is working correctly!</p>
            </body>
        </html>
        """

        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        message.attach(part1)
        message.attach(part2)

        # Connect and send
        if test_config['smtp_use_ssl']:
            server = smtplib.SMTP_SSL(test_config['smtp_server'], test_config['smtp_port'])
        else:
            server = smtplib.SMTP(test_config['smtp_server'], test_config['smtp_port'])
            if test_config['smtp_use_tls']:
                server.starttls()

        server.login(test_config['smtp_username'], test_config['smtp_password'])
        server.sendmail(test_config['sender_email'], test_email, message.as_string())
        server.quit()

        return jsonify({
            'success': True,
            'message': f'Test email sent successfully to {test_email}'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to send test email: {str(e)}'
        }), 500


@bp.route('/config/<int:config_id>', methods=['DELETE'])
@super_admin_required
def delete_smtp_config(config_id):
    """Delete SMTP configuration (super admin only)"""
    config = SMTPConfig.query.get_or_404(config_id)

    db.session.delete(config)
    db.session.commit()

    return jsonify({'message': 'SMTP configuration deleted successfully'})
