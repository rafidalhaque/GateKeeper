"""
CLI commands for GateKeeper
"""
import click
import uuid
import secrets
from flask import current_app
from app.models import db
from app.models.auth import Role, Permission, AdminUser
from app.models.events import Event


def register_commands(app):
    """Register CLI commands with the Flask app"""
    
    @app.cli.command('seed-permissions')
    def seed_permissions():
        """Seed system permissions (auto-generated, non-deletable)"""
        click.echo('Seeding permissions...')
        
        permissions_data = [
            # Dashboard
            ('dashboard.view', 'View dashboard statistics', 'dashboard'),

            # Participants
            ('participant.read', 'Read participant data', 'participants'),
            ('participant.create', 'Create participants', 'participants'),
            ('participant.update', 'Update participants', 'participants'),
            ('participant.delete', 'Delete participants', 'participants'),
            
            # Teams
            ('team.read', 'Read team data', 'teams'),
            ('team.create', 'Create teams', 'teams'),
            ('team.update', 'Update teams', 'teams'),
            ('team.delete', 'Delete teams', 'teams'),
            
            # Attendance
            ('attendance.read', 'Read attendance data', 'attendance'),
            ('attendance.mark', 'Mark attendance', 'attendance'),
            
            # Tickets
            ('ticket.read', 'Read ticket data', 'tickets'),
            ('ticket.generate', 'Generate tickets', 'tickets'),
            ('ticket.send', 'Send tickets', 'tickets'),
            
            # Emails
            ('email.read_logs', 'Read email logs', 'emails'),
            ('email.send_bulk', 'Send bulk emails', 'emails'),
            
            # Email Templates
            ('email_template.read', 'Read email templates', 'email_templates'),
            ('email_template.create', 'Create email templates', 'email_templates'),
            ('email_template.update', 'Update email templates', 'email_templates'),
            ('email_template.delete', 'Delete email templates', 'email_templates'),
            ('email_template.test', 'Send test emails', 'email_templates'),

            # CSV Import
            ('csv.import', 'Import CSV data', 'csv'),
            
            # Events
            ('event.read', 'Read event data', 'events'),
            ('event.create', 'Create events', 'events'),
            ('event.update', 'Update events', 'events'),
            ('event.delete', 'Delete events', 'events'),
            ('event.configure', 'Configure event settings', 'events'),
            
            # Roles & Permissions
            ('role.read', 'Read roles', 'roles'),
            ('role.create', 'Create roles', 'roles'),
            ('role.update', 'Update roles', 'roles'),
            ('role.delete', 'Delete roles', 'roles'),
            ('permission.read', 'Read permissions', 'permissions'),
            
            # Reports
            ('report.read', 'Read reports', 'reports'),
            ('report.export', 'Export reports', 'reports'),
        ]
        
        for key, description, feature_group in permissions_data:
            permission = Permission.query.filter_by(key=key).first()
            if not permission:
                permission = Permission(
                    key=key,
                    description=description,
                    feature_group=feature_group,
                    system_reserved=True
                )
                db.session.add(permission)
                click.echo(f'  Created permission: {key}')
        
        db.session.commit()
        click.echo('Permissions seeded successfully!')
    
    @app.cli.command('seed-roles')
    def seed_roles():
        """Seed default roles"""
        click.echo('Seeding default roles...')
        
        # Super Admin role (all permissions)
        super_admin_role = Role.query.filter_by(name='Super Admin').first()
        if not super_admin_role:
            super_admin_role = Role(
                name='Super Admin',
                description='Full system access with all permissions'
            )
            db.session.add(super_admin_role)
            click.echo('  Created role: Super Admin')
        
        # Event Admin role
        event_admin_role = Role.query.filter_by(name='Event Admin').first()
        if not event_admin_role:
            event_admin_role = Role(
                name='Event Admin',
                description='Full event and participant management access'
            )
            db.session.add(event_admin_role)
            
            # Assign permissions
            event_admin_permissions = [
                'dashboard.view',
                'participant.read', 'participant.create', 'participant.update', 'participant.delete',
                'team.read', 'team.create', 'team.update', 'team.delete',
                'attendance.read', 'attendance.mark',
                'ticket.read', 'ticket.generate', 'ticket.send',
                'email.read_logs', 'email.send_bulk',
                'email_template.read', 'email_template.create', 'email_template.update',
                'email_template.delete', 'email_template.test',
                'csv.import',
                'event.read', 'event.update', 'event.configure',
                'report.read', 'report.export'
            ]
            
            for perm_key in event_admin_permissions:
                perm = Permission.query.filter_by(key=perm_key).first()
                if perm:
                    event_admin_role.permissions.append(perm)
            
            click.echo('  Created role: Event Admin')
        
        # Booth Manager role
        booth_manager_role = Role.query.filter_by(name='Booth Manager').first()
        if not booth_manager_role:
            booth_manager_role = Role(
                name='Booth Manager',
                description='Limited access for check-in operations'
            )
            db.session.add(booth_manager_role)
            
            # Assign permissions
            booth_manager_permissions = [
                'participant.read',
                'attendance.read',
                'attendance.mark'
            ]
            
            for perm_key in booth_manager_permissions:
                perm = Permission.query.filter_by(key=perm_key).first()
                if perm:
                    booth_manager_role.permissions.append(perm)
            
            click.echo('  Created role: Booth Manager')
        
        db.session.commit()
        click.echo('Roles seeded successfully!')
    
    @app.cli.command('create-admin')
    @click.option('--email', prompt='Email', help='Admin email address')
    @click.option('--name', prompt='Name', help='Admin name')
    @click.option('--role', default='Event Admin', help='Role name (default: Event Admin)')
    def create_admin(email, name, role):
        """Create an admin user that will be linked to a Supabase account"""
        click.echo(f'Creating admin user: {email}')

        # Check if user already exists
        existing_user = AdminUser.query.filter_by(email=email).first()
        if existing_user:
            click.echo('Error: User with this email already exists!')
            return

        # Find the role
        user_role = Role.query.filter_by(name=role).first()
        if not user_role:
            click.echo(f'Error: Role "{role}" not found!')
            click.echo('Available roles:')
            for r in Role.query.all():
                click.echo(f'  - {r.name}')
            return

        # Create admin user (without Supabase ID - will be linked on first login)
        admin_user = AdminUser(
            supabase_user_id=None,  # Will be set when user first logs in
            email=email,
            name=name,
            role_id=user_role.id,
            is_super_admin=False
        )

        db.session.add(admin_user)
        db.session.commit()

        click.echo(f'Admin user created successfully!')
        click.echo(f'  Email: {email}')
        click.echo(f'  Name: {name}')
        click.echo(f'  Role: {role}')
        click.echo('\nThe user can now sign in with their Supabase account using this email.')
        click.echo('On first login, their Supabase ID will be automatically linked.')


    @app.cli.command('create-super-admin')
    @click.option('--email', prompt='Email', help='Admin email address')
    @click.option('--name', prompt='Name', help='Admin name')
    def create_super_admin(email, name):
        """Create a super admin user (CLI recommended method)"""
        click.echo(f'Creating super admin: {email}')
        
        # Check if user already exists
        existing_user = AdminUser.query.filter_by(email=email).first()
        if existing_user:
            click.echo('Error: User with this email already exists!')
            return
        
        # Create admin user (without Supabase ID - will be linked on first login)
        admin_user = AdminUser(
            supabase_user_id=None,  # Will be set when user first logs in
            email=email,
            name=name,
            is_super_admin=True
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        click.echo(f'Super admin created successfully!')
        click.echo(f'  Email: {email}')
        click.echo(f'  Name: {name}')
        click.echo('\nThe user can now sign in with their Supabase account using this email.')
        click.echo('On first login, their Supabase ID will be automatically linked.')
