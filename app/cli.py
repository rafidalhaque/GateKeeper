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
                'participant.read', 'participant.create', 'participant.update', 'participant.delete',
                'team.read', 'team.create', 'team.update', 'team.delete',
                'attendance.read', 'attendance.mark',
                'ticket.read', 'ticket.generate', 'ticket.send',
                'email.read_logs', 'email.send_bulk',
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
        
        # Generate a unique Supabase user ID (in production, this would come from Supabase)
        # For now, we'll use a UUID with a prefix
        supabase_user_id = f'super-admin-{uuid.uuid4()}'
        
        # Create admin user
        admin_user = AdminUser(
            supabase_user_id=supabase_user_id,
            email=email,
            name=name,
            is_super_admin=True
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        click.echo(f'Super admin created successfully!')
        click.echo(f'  Email: {email}')
        click.echo(f'  Name: {name}')
        click.echo(f'  Supabase User ID: {supabase_user_id}')
        click.echo('\nNote: This user needs to be created in Supabase Auth separately.')
        click.echo('In production, integrate with Supabase API to create the auth user.')
