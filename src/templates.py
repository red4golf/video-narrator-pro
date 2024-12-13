import json
from pathlib import Path

class NarrationTemplate:
    def __init__(self, id, name, description, analysis_prompt, narration_prompt):
        self.id = id
        self.name = name
        self.description = description
        self._default_analysis_prompt = analysis_prompt
        self._default_narration_prompt = narration_prompt
        self._custom_analysis_prompt = None
        self._custom_narration_prompt = None

    @property
    def analysis_prompt(self):
        return self._custom_analysis_prompt or self._default_analysis_prompt

    @analysis_prompt.setter
    def analysis_prompt(self, value):
        self._custom_analysis_prompt = value

    @property
    def narration_prompt(self):
        return self._custom_narration_prompt or self._default_narration_prompt

    @narration_prompt.setter
    def narration_prompt(self, value):
        self._custom_narration_prompt = value

    def reset_to_defaults(self):
        """Reset prompts to default values"""
        self._custom_analysis_prompt = None
        self._custom_narration_prompt = None

    def has_custom_prompts(self):
        """Check if template has custom prompts"""
        return bool(self._custom_analysis_prompt or self._custom_narration_prompt)

    def to_dict(self):
        """Convert template to dictionary for saving"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'custom_analysis_prompt': self._custom_analysis_prompt,
            'custom_narration_prompt': self._custom_narration_prompt
        }

    @classmethod
    def from_dict(cls, data, default_template):
        """Create template from dictionary with defaults"""
        template = cls(
            id=default_template.id,
            name=default_template.name,
            description=default_template.description,
            analysis_prompt=default_template._default_analysis_prompt,
            narration_prompt=default_template._default_narration_prompt
        )
        if data.get('custom_analysis_prompt'):
            template._custom_analysis_prompt = data['custom_analysis_prompt']
        if data.get('custom_narration_prompt'):
            template._custom_narration_prompt = data['custom_narration_prompt']
        return template

class TemplateManager:
    def __init__(self):
        self.templates = {}
        self._initialize_templates()
        self.load_custom_prompts()

    def _initialize_templates(self):
        # Room Walk-through Template
        self.templates['room-tour'] = NarrationTemplate(
            id='room-tour',
            name='Room Walk-through',
            description='Perfect for real estate, hotel rooms, and interior tours',
            analysis_prompt="""Analyze this room as a veteran tour guide would see it. Focus on:
                - Layout and practical use of space
                - Notable features or amenities
                - Lighting and atmosphere
                - Quality of finishes and materials
                Describe it clearly and directly, as if explaining to a friend.""",
            narration_prompt="""Create a natural, flowing tour narrative connecting these room descriptions.
                Use a straightforward, conversational style appropriate for a veteran narrator.
                Focus on practical details and clear transitions between spaces."""
        )

        # Add other default templates...
        [Previous template definitions remain the same...]

    def save_custom_prompts(self):
        """Save custom prompts to file"""
        custom_data = {
            template_id: template.to_dict() 
            for template_id, template in self.templates.items() 
            if template.has_custom_prompts()
        }
        
        if custom_data:
            save_path = Path('custom_prompts.json')
            with open(save_path, 'w') as f:
                json.dump(custom_data, f, indent=2)

    def load_custom_prompts(self):
        """Load custom prompts from file"""
        try:
            load_path = Path('custom_prompts.json')
            if load_path.exists():
                with open(load_path, 'r') as f:
                    custom_data = json.load(f)
                
                for template_id, data in custom_data.items():
                    if template_id in self.templates:
                        self.templates[template_id] = NarrationTemplate.from_dict(
                            data, self.templates[template_id]
                        )
        except Exception as e:
            print(f"Error loading custom prompts: {e}")

    [Previous methods remain the same...]