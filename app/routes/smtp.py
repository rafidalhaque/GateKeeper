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

    # Check if updating existing config
    existing_config = SMTPConfig.query.filter_by(is_active=True).first()

    # Validate required fields (password not required if updating existing config)
    if existing_config:
        required_fields = ['smtp_server', 'smtp_port', 'smtp_username', 'sender_email']
    else:
        required_fields = ['smtp_server', 'smtp_port', 'smtp_username', 'smtp_password', 'sender_email']

    missing_fields = [field for field in required_fields if not data.get(field)]

    if missing_fields:
        return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

    # Get password: use provided password or keep existing one
    password = data.get('smtp_password')
    if not password and existing_config:
        password = existing_config.smtp_password
    elif not password:
        return jsonify({'error': 'Password is required for new configuration'}), 400

    # Deactivate any existing configs
    SMTPConfig.query.update({'is_active': False})

    # Create new config
    config = SMTPConfig(
        smtp_server=data['smtp_server'],
        smtp_port=data['smtp_port'],
        smtp_username=data['smtp_username'],
        smtp_password=password,  # Use provided or existing password
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

    # Get active config from database
    config = SMTPConfig.query.filter_by(is_active=True).first()

    if not config and 'smtp_server' not in data:
        return jsonify({'error': 'No SMTP configuration found'}), 400

    # Use provided config for testing, but IMPORTANT:
    # If password is empty in data, use password from database
    submitted_password = data.get('smtp_password', '')

    # Use database password if submitted password is empty (security: password hidden in frontend)
    actual_password = submitted_password if submitted_password else (config.smtp_password if config else None)

    test_config = {
        'smtp_server': data.get('smtp_server', config.smtp_server if config else None),
        'smtp_port': data.get('smtp_port', config.smtp_port if config else 587),
        'smtp_username': data.get('smtp_username', config.smtp_username if config else None),
        'smtp_password': actual_password,  # Use actual password from DB if not provided
        'smtp_use_tls': data.get('smtp_use_tls', config.smtp_use_tls if config else True),
        'smtp_use_ssl': data.get('smtp_use_ssl', config.smtp_use_ssl if config else False),
        'sender_email': data.get('sender_email', config.sender_email if config else None),
        'sender_name': data.get('sender_name', config.sender_name if config else 'GateKeeper')
    }

    # Validate we have a password
    if not test_config['smtp_password']:
        return jsonify({
            'error': 'Missing SMTP password',
            'help': 'Please enter your SMTP password or save the configuration first.'
        }), 400

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
        try:
            if test_config['smtp_use_ssl']:
                server = smtplib.SMTP_SSL(test_config['smtp_server'], test_config['smtp_port'], timeout=10)
            else:
                server = smtplib.SMTP(test_config['smtp_server'], test_config['smtp_port'], timeout=10)
                if test_config['smtp_use_tls']:
                    server.starttls()

            server.login(test_config['smtp_username'], test_config['smtp_password'])
            server.sendmail(test_config['sender_email'], test_email, message.as_string())
            server.quit()

            return jsonify({
                'success': True,
                'message': f'Test email sent successfully to {test_email}'
            })

        except smtplib.SMTPAuthenticationError as e:
            # Authentication failed
            error_msg = str(e)
            help_msg = ""

            if 'gmail.com' in test_config['smtp_server'].lower():
                help_msg = (
                    "Gmail authentication failed. Common fixes:\n\n"
                    "1. Use an App Password instead of your regular password:\n"
                    "   - Go to Google Account → Security → 2-Step Verification → App passwords\n"
                    "   - Generate a new app password for 'Mail'\n"
                    "   - Use that 16-character password instead\n\n"
                    "2. Enable 'Less secure app access' (not recommended):\n"
                    "   - Go to https://myaccount.google.com/lesssecureapps\n\n"
                    "3. Make sure 2-Factor Authentication is enabled (required for App Passwords)"
                )
            else:
                help_msg = (
                    "SMTP authentication failed. Please check:\n\n"
                    "1. Username and password are correct\n"
                    "2. Your email provider allows SMTP access\n"
                    "3. You may need an app-specific password\n"
                    "4. Check if 2FA is required"
                )

            return jsonify({
                'success': False,
                'error': f'Authentication Error: {error_msg}',
                'help': help_msg
            }), 401

        except smtplib.SMTPConnectError as e:
            return jsonify({
                'success': False,
                'error': f'Connection Error: Cannot connect to {test_config["smtp_server"]}:{test_config["smtp_port"]}',
                'help': 'Check that the server address and port are correct. Common ports: 587 (TLS), 465 (SSL), 25 (Plain)'
            }), 500

        except smtplib.SMTPServerDisconnected as e:
            return jsonify({
                'success': False,
                'error': 'Server disconnected unexpectedly',
                'help': 'The SMTP server closed the connection. This might be due to incorrect TLS/SSL settings or firewall issues.'
            }), 500

        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'SMTP Error: {str(e)}',
                'help': 'Check your SMTP settings and try again.'
            }), 500

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
