#!/usr/bin/env python3
"""
🤖 IMPROVED SYNTHETIC DATA GENERATOR
Generates high-variety synthetic examples with minimal duplicates
"""

import random
import hashlib
from typing import List, Dict, Set

class ImprovedSyntheticGenerator:
    """Generate diverse synthetic examples with duplicate prevention"""
    
    def __init__(self):
        self.generated_hashes: Set[str] = set()
        self.label_mapping = {
            'SAVE_MEMORY': 0,
            'SEARCH_MEMORY': 1,
            'NO_ACTION': 2
        }
        
        # Much larger template variety
        self.templates = {
            'SAVE_MEMORY': [
                # Technical solutions
                "Remember: {technical_solution}",
                "Solution found: {technical_solution}",
                "Fixed issue: {technical_solution}",
                "Important fix: {technical_solution}",
                "Save this: {technical_solution}",
                "Document: {technical_solution}",
                "Archive: {technical_solution}",
                "Store solution: {technical_solution}",
                
                # Configuration saves
                "Config: {config_detail}",
                "Setting: {config_detail}",
                "Configuration saved: {config_detail}",
                "Environment: {config_detail}",
                "Parameter: {config_detail}",
                
                # Italian versions
                "Ricorda: {technical_solution}",
                "Soluzione trovata: {technical_solution}",
                "Problema risolto: {technical_solution}",
                "Importante: {technical_solution}",
                "Salva questo: {technical_solution}",
                "Documenta: {technical_solution}",
                "Archivia: {technical_solution}",
                "Configurazione: {config_detail}",
                "Impostazione: {config_detail}",
                "Parametro: {config_detail}",
                
                # Complex patterns
                "I solved {problem_type} using {solution_method}",
                "Fixed {technical_issue} with {fix_approach}",
                "Resolved {system_problem} by {resolution_method}",
                "Ho risolto {problem_type} usando {solution_method}",
                "Risolto {technical_issue} con {fix_approach}",
                "Sistemato {system_problem} tramite {resolution_method}",
            ],
            
            'SEARCH_MEMORY': [
                # Questions
                "How to {technical_task}?",
                "How can I {technical_task}?",
                "What's the best way to {technical_task}?",
                "Help with {technical_problem}",
                "Need help with {technical_problem}",
                "Looking for {search_target}",
                "Where is {search_target}?",
                "Find {search_target}",
                "Search for {search_target}",
                
                # Italian questions
                "Come {technical_task}?",
                "Come posso {technical_task}?",
                "Qual è il modo migliore per {technical_task}?",
                "Aiuto con {technical_problem}",
                "Ho bisogno di aiuto con {technical_problem}",
                "Cerco {search_target}",
                "Dove si trova {search_target}?",
                "Trova {search_target}",
                "Cerca {search_target}",
                
                # Problem-based
                "Error: {error_type}",
                "Issue: {technical_problem}",
                "Problem: {technical_problem}",
                "Bug: {technical_problem}",
                "Trouble with: {technical_problem}",
                "Errore: {error_type}",
                "Problema: {technical_problem}",
                "Bug: {technical_problem}",
                "Difficoltà con: {technical_problem}",
                
                # Past references
                "What was the fix for {past_issue}?",
                "How did I solve {past_issue}?",
                "Previous solution for {past_issue}?",
                "Qual era la soluzione per {past_issue}?",
                "Come ho risolto {past_issue}?",
                "Soluzione precedente per {past_issue}?",
            ],
            
            'NO_ACTION': [
                # Greetings and social
                "Hello!", "Hi there!", "Good morning!", "Good afternoon!", "Good evening!",
                "Thanks!", "Thank you!", "Thanks a lot!", "Much appreciated!",
                "OK", "Okay", "Alright", "Sure", "Perfect", "Great!",
                "Yes", "No", "Maybe", "Possibly", "Definitely", "Absolutely",
                "I see", "I understand", "Got it", "Makes sense", "Right",
                "Bye!", "Goodbye!", "See you!", "Talk later!", "Have a nice day!",
                
                # Italian social
                "Ciao!", "Salve!", "Buongiorno!", "Buonasera!", "Buonanotte!",
                "Grazie!", "Grazie mille!", "Molto gentile!", "Apprezzato!",
                "OK", "Va bene", "D'accordo", "Sicuro", "Perfetto", "Ottimo!",
                "Sì", "No", "Forse", "Possibilmente", "Definitivamente", "Assolutamente",
                "Capisco", "Ho capito", "Chiaro", "Ha senso", "Giusto",
                "Ciao!", "Arrivederci!", "Ci sentiamo!", "Buona giornata!",
                
                # Random non-technical
                "Weather is nice today", "I like coffee", "Weekend plans?",
                "What time is it?", "How's your day?", "Feeling good today",
                "Music sounds great", "Movie was interesting", "Book recommendation?",
                "Travel plans?", "Food looks delicious", "Exercise is important",
                
                # Italian non-technical
                "Bel tempo oggi", "Mi piace il caffè", "Piani per il weekend?",
                "Che ore sono?", "Come va la giornata?", "Mi sento bene oggi",
                "Bella musica", "Film interessante", "Libri da consigliare?",
                "Piani di viaggio?", "Cibo delizioso", "L'esercizio è importante",
            ]
        }
        
        # Expanded vocabularies with more variety
        self.vocabularies = {
            'technical_solution': [
                'use Redis for caching with 1-hour TTL',
                'implement JWT authentication with refresh tokens',
                'add database connection pooling (max 20 connections)',
                'configure nginx reverse proxy with SSL',
                'use Docker multi-stage builds for smaller images',
                'implement circuit breaker pattern for API calls',
                'add request rate limiting (100 req/min per user)',
                'use CDN for static assets with 24h cache',
                'implement database migrations with rollback support',
                'add comprehensive logging with structured JSON',
                'use environment variables for configuration',
                'implement health checks for container orchestration',
                'add retry logic with exponential backoff',
                'use blue-green deployment for zero downtime',
                'implement API versioning with proper headers',
                'add monitoring with Prometheus and Grafana',
                'use database indexing for query optimization',
                'implement proper CORS headers for browser security',
                'add input validation and sanitization',
                'use message queues for async processing',
            ],
            
            'config_detail': [
                'DATABASE_URL=postgresql://user:pass@localhost:5432/db',
                'REDIS_URL=redis://localhost:6379/0',
                'JWT_SECRET=random-256-bit-key-here',
                'API_RATE_LIMIT=1000',
                'CACHE_TTL=3600',
                'MAX_CONNECTIONS=20',
                'TIMEOUT=30000',
                'LOG_LEVEL=info',
                'NODE_ENV=production',
                'PORT=8080',
                'SSL_CERT_PATH=/certs/server.crt',
                'SSL_KEY_PATH=/certs/server.key',
                'BACKUP_SCHEDULE=0 2 * * *',
                'MONITORING_ENABLED=true',
                'DEBUG_MODE=false',
            ],
            
            'technical_task': [
                'implement user authentication',
                'optimize database queries',
                'deploy to production',
                'configure load balancing',
                'set up monitoring',
                'implement caching',
                'handle API errors',
                'manage state in React',
                'configure CI/CD pipeline',
                'implement search functionality',
                'optimize React performance',
                'handle file uploads',
                'implement real-time updates',
                'configure SSL certificates',
                'manage Docker containers',
                'implement data validation',
                'optimize bundle size',
                'handle concurrent requests',
                'implement logging',
                'configure backup strategy',
            ],
            
            'technical_problem': [
                'slow database queries',
                'memory leaks in React',
                'CORS errors in browser',
                'authentication failures',
                'timeout issues',
                'container startup problems',
                'high CPU usage',
                'API rate limiting',
                'cache invalidation',
                'SSL certificate errors',
                'database connection drops',
                'React component re-renders',
                'bundle size too large',
                'server response delays',
                'WebSocket connection issues',
                'Docker image build failures',
                'NPM dependency conflicts',
                'TypeScript compilation errors',
                'Test suite timeouts',
                'Production deployment issues',
            ],
            
            'search_target': [
                'user authentication implementation',
                'database optimization guide',
                'React performance tips',
                'Docker configuration',
                'API error handling',
                'caching strategy',
                'monitoring setup',
                'SSL configuration',
                'backup procedures',
                'deployment scripts',
                'logging configuration',
                'security best practices',
                'testing strategies',
                'code review guidelines',
                'performance benchmarks',
            ],
            
            'error_type': [
                'ConnectionError',
                'TimeoutError',
                'AuthenticationError',
                'ValidationError',
                'NetworkError',
                'DatabaseError',
                'CacheError',
                'ConfigurationError',
                'PermissionError',
                'RateLimitError',
            ],
            
            'problem_type': [
                'performance bottleneck',
                'security vulnerability',
                'scalability issue',
                'integration problem',
                'configuration error',
                'dependency conflict',
                'deployment failure',
                'data corruption',
                'service outage',
                'synchronization issue',
            ],
            
            'solution_method': [
                'implementing connection pooling',
                'adding caching layer',
                'optimizing database queries',
                'using load balancing',
                'implementing retry logic',
                'adding monitoring',
                'upgrading dependencies',
                'refactoring code architecture',
                'implementing circuit breaker',
                'using message queues',
            ],
            
            'technical_issue': [
                'API response timeouts',
                'memory usage spikes',
                'database deadlocks',
                'authentication token expiry',
                'CORS policy violations',
                'SSL handshake failures',
                'container resource limits',
                'network connectivity issues',
                'data serialization errors',
                'WebSocket connection drops',
            ],
            
            'fix_approach': [
                'increasing timeout values',
                'implementing memory cleanup',
                'adding database indexes',
                'using refresh tokens',
                'configuring proper headers',
                'updating SSL certificates',
                'adjusting resource limits',
                'implementing retry mechanisms',
                'fixing serialization logic',
                'improving connection handling',
            ],
            
            'system_problem': [
                'high memory consumption',
                'slow response times',
                'frequent disconnections',
                'unstable performance',
                'security vulnerabilities',
                'data inconsistencies',
                'service unavailability',
                'resource exhaustion',
                'configuration drift',
                'monitoring blind spots',
            ],
            
            'resolution_method': [
                'implementing monitoring',
                'optimizing algorithms',
                'improving connection management',
                'adding performance tuning',
                'upgrading security measures',
                'implementing data validation',
                'adding redundancy',
                'optimizing resource usage',
                'implementing configuration management',
                'enhancing observability',
            ],
            
            'past_issue': [
                'slow login process',
                'database connection errors',
                'React rendering problems',
                'Docker deployment failures',
                'API authentication issues',
                'cache invalidation problems',
                'SSL certificate renewal',
                'High server load',
                'Memory leak detection',
                'Performance degradation',
            ]
        }
    
    def _generate_hash(self, text: str) -> str:
        """Generate hash for duplicate detection"""
        return hashlib.md5(text.lower().strip().encode()).hexdigest()
    
    def _fill_template(self, template: str) -> str:
        """Fill template with random vocabulary, ensuring uniqueness"""
        text = template
        
        # Fill placeholders
        for placeholder, options in self.vocabularies.items():
            if f'{{{placeholder}}}' in text:
                text = text.replace(f'{{{placeholder}}}', random.choice(options))
        
        # Add some randomization to prevent duplicates
        if random.random() < 0.1:  # 10% chance to add prefix/suffix
            if random.random() < 0.5:
                prefixes = ["Actually, ", "Well, ", "So, ", "Basically, ", "Essentially, "]
                text = random.choice(prefixes) + text.lower()
            else:
                suffixes = [" please", " thanks", " now", " today", " here"]
                text = text + random.choice(suffixes)
        
        return text
    
    def generate_unique_examples(self, target_count: int, action: str, max_attempts: int = 5) -> List[Dict]:
        """Generate unique examples for a specific action"""
        examples = []
        attempts = 0
        templates = self.templates[action]
        
        while len(examples) < target_count and attempts < max_attempts:
            attempts += 1
            
            for _ in range(target_count - len(examples)):
                # Pick random template
                template = random.choice(templates)
                
                # Fill template
                text = self._fill_template(template)
                
                # Check for duplicates
                text_hash = self._generate_hash(text)
                if text_hash not in self.generated_hashes:
                    self.generated_hashes.add(text_hash)
                    
                    examples.append({
                        'text': text,
                        'label': self.label_mapping[action],
                        'label_name': action,
                        'source': 'synthetic',
                        'language': 'italian' if any(word in text.lower() for word in 
                                   ['ricorda', 'come', 'dove', 'quando', 'che', 'con', 'per']) else 'english'
                    })
                
                if len(examples) >= target_count:
                    break
        
        return examples
    
    def generate_dataset(self, target_size: int) -> List[Dict]:
        """Generate full synthetic dataset with target distribution"""
        
        # Target distribution
        save_count = int(target_size * 0.4)
        search_count = int(target_size * 0.35)
        no_action_count = target_size - save_count - search_count
        
        all_examples = []
        
        print(f"🤖 Generating {target_size:,} synthetic examples...")
        print(f"  SAVE_MEMORY: {save_count:,}")
        print(f"  SEARCH_MEMORY: {search_count:,}")
        print(f"  NO_ACTION: {no_action_count:,}")
        
        # Generate each category
        save_examples = self.generate_unique_examples(save_count, 'SAVE_MEMORY')
        all_examples.extend(save_examples)
        print(f"  ✅ Generated {len(save_examples):,} SAVE_MEMORY examples")
        
        search_examples = self.generate_unique_examples(search_count, 'SEARCH_MEMORY')
        all_examples.extend(search_examples)
        print(f"  ✅ Generated {len(search_examples):,} SEARCH_MEMORY examples")
        
        no_action_examples = self.generate_unique_examples(no_action_count, 'NO_ACTION')
        all_examples.extend(no_action_examples)
        print(f"  ✅ Generated {len(no_action_examples):,} NO_ACTION examples")
        
        print(f"\n🎯 Total generated: {len(all_examples):,} unique examples")
        print(f"🔄 Duplicates prevented: {len(self.generated_hashes)} unique hashes tracked")
        
        return all_examples

def test_generator():
    """Test the improved generator"""
    
    print("🧪 **TESTING IMPROVED SYNTHETIC GENERATOR**")
    print("=" * 50)
    
    generator = ImprovedSyntheticGenerator()
    
    # Generate a small test set
    test_examples = generator.generate_dataset(1000)
    
    # Check uniqueness
    texts = [ex['text'] for ex in test_examples]
    unique_texts = set(texts)
    
    print(f"\n📊 **UNIQUENESS TEST**")
    print(f"Generated: {len(texts):,} examples")
    print(f"Unique: {len(unique_texts):,} examples")
    print(f"Duplicate rate: {(len(texts) - len(unique_texts)) / len(texts) * 100:.2f}%")
    
    # Show samples
    print(f"\n📝 **SAMPLE EXAMPLES**")
    for i, example in enumerate(test_examples[:10], 1):
        print(f"{i:2d}. \"{example['text']}\" ({example['label_name']}, {example['language']})")
    
    return test_examples

if __name__ == "__main__":
    test_examples = test_generator()
