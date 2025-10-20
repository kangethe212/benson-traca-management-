from django.core.management.base import BaseCommand
from listings.models import Agent

class Command(BaseCommand):
    help = 'Check all agents in the database'

    def handle(self, *args, **options):
        agents = Agent.objects.all()
        
        self.stdout.write(f'Total agents: {agents.count()}')
        self.stdout.write('=' * 50)
        
        for agent in agents:
            self.stdout.write(f'Agent: {agent.full_name}')
            self.stdout.write(f'  - Username: {agent.user.username}')
            self.stdout.write(f'  - Active: {agent.is_active}')
            self.stdout.write(f'  - Verified: {agent.is_verified}')
            self.stdout.write(f'  - Phone: {agent.phone}')
            self.stdout.write(f'  - Bio: {agent.bio[:50] if agent.bio else "No bio"}...')
            self.stdout.write('-' * 30)
        
        # Check for John Mwangi specifically
        john_agents = Agent.objects.filter(
            user__first_name__icontains='john',
            user__last_name__icontains='mwangi'
        )
        
        self.stdout.write(f'John Mwangi agents found: {john_agents.count()}')
        for agent in john_agents:
            self.stdout.write(f'Found John Mwangi: {agent.full_name} (ID: {agent.pk})')
