"""
Template management for Video Narrator Pro.
Handles template definitions, customization, and persistence.
"""

import json
from pathlib import Path
import logging
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict

@dataclass
class Template:
    """Individual template with default and custom prompts"""
    id: str
    name: str
    description: str
    default_analysis_prompt: str
    default_narration_prompt: str
    custom_analysis_prompt: Optional[str] = None
    custom_narration_prompt: Optional[str] = None

    @property
    def analysis_prompt(self) -> str:
        """Get active analysis prompt"""
        return self.custom_analysis_prompt or self.default_analysis_prompt

    @property
    def narration_prompt(self) -> str:
        """Get active narration prompt"""
        return self.custom_narration_prompt or self.default_narration_prompt

    def reset_to_defaults(self) -> None:
        """Reset to default prompts"""
        self.custom_analysis_prompt = None
        self.custom_narration_prompt = None

    def is_customized(self) -> bool:
        """Check if template has custom prompts"""
        return bool(self.custom_analysis_prompt or self.custom_narration_prompt)

    def to_dict(self) -> dict:
        """Convert template to dictionary for saving"""
        return {
            'id': self.id,
            'custom_analysis_prompt': self.custom_analysis_prompt,
            'custom_narration_prompt': self.custom_narration_prompt
        }

    @classmethod
    def from_dict(cls, data: dict, default_template: 'Template') -> 'Template':
        """Create template from dictionary with defaults"""
        return cls(
            id=default_template.id,
            name=default_template.name,
            description=default_template.description,
            default_analysis_prompt=default_template.default_analysis_prompt,
            default_narration_prompt=default_template.default_narration_prompt,
            custom_analysis_prompt=data.get('custom_analysis_prompt'),
            custom_narration_prompt=data.get('custom_narration_prompt')
        )

class TemplateManager:
    """Manages template collection and persistence"""
    
    def __init__(self):
        self.templates: Dict[str, Template] = {}
        self._initialize_defaults()
        self.load_custom_prompts()

    def _initialize_defaults(self) -> None:
        """Initialize default templates"""
        self.templates['room-tour'] = Template(
            id='room-tour',
            name='Room Walk-through',
            description='Perfect for real estate, hotel rooms, and interior tours',
            default_analysis_prompt="""
            Analyze this room as a veteran tour guide would see it. Focus on:
            - Layout and practical use of space
            - Notable features and amenities
            - Lighting and atmosphere
            - Quality of finishes and materials
            Describe it clearly and directly, as if explaining to a friend.
            """.strip(),
            default_narration_prompt="""
            Create a natural, flowing tour narrative connecting these room descriptions.
            Use a straightforward, conversational style appropriate for a veteran narrator.
            Focus on practical details and clear transitions between spaces.
            """.strip()
        )

        self.templates['outdoor-scene'] = Template(
            id='outdoor-scene',
            name='Outdoor Scenes',
            description='Ideal for nature, landscapes, and exterior property views',
            default_analysis_prompt="""
            Observe this outdoor scene as an experienced guide would.
            Note key features like:
            - Landscape elements and views
            - Natural features and terrain
            - Notable landmarks or structures
            - Weather and lighting conditions
            Use clear, straightforward language.
            """.strip(),
            default_narration_prompt="""
            Develop a natural narrative that guides viewers through these outdoor scenes.
            Use direct, clear language that connects different views and locations.
            Focus on notable features and maintain a steady, comfortable pace.
            """.strip()
        )

        self.templates['event-coverage'] = Template(
            id='event-coverage',
            name='Event Coverage',
            description='Great for ceremonies, gatherings, and special occasions',
            default_analysis_prompt="""
            Analyze this event scene focusing on:
            - Key activities and moments
            - People and interactions
            - Setting and atmosphere
            - Timeline of events
            Describe it clearly and chronologically.
            """.strip(),
            default_narration_prompt="""
            Create a chronological narrative of the event that flows naturally.
            Focus on key moments and transitions.
            Maintain clear timing references while keeping a conversational tone.
            """.strip()
        )

        self.templates['product-showcase'] = Template(
            id='product-showcase',
            name='Product Showcase',
            description='Suited for product demonstrations and features',
            default_analysis_prompt="""
            Examine this product scene focusing on:
            - Key features and functions
            - Design elements
            - Practical benefits
            - Quality and craftsmanship
            Use clear, non-marketing language.
            """.strip(),
            default_narration_prompt="""
            Develop a straightforward narrative about the product's features and benefits.
            Avoid marketing jargon and focus on practical information.
            Create natural transitions between different aspects of the product.
            """.strip()
        )

    def get_template(self, template_id: str) -> Optional[Template]:
        """Get template by ID"""
        return self.templates.get(template_id)

    def get_template_by_name(self, name: str) -> Optional[Template]:
        """Get template by name"""
        return next((t for t in self.templates.values() if t.name == name), None)

    def get_template_names(self) -> List[str]:
        """Get list of template names"""
        return [t.name for t in self.templates.values()]

    def get_template_descriptions(self) -> Dict[str, str]:
        """Get dictionary of template names and descriptions"""
        return {t.name: t.description for t in self.templates.values()}

    def save_custom_prompts(self) -> None:
        """Save custom prompts to file"""
        try:
            custom_data = {
                template_id: template.to_dict()
                for template_id, template in self.templates.items()
                if template.is_customized()
            }

            if custom_data:
                save_path = Path('custom_prompts.json')
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump(custom_data, f, indent=2)
                    
        except Exception as e:
            logging.error(f"Error saving custom prompts: {e}")
            raise

    def load_custom_prompts(self) -> None:
        """Load custom prompts from file"""
        try:
            load_path = Path('custom_prompts.json')
            if not load_path.exists():
                return

            with open(load_path, 'r', encoding='utf-8') as f:
                custom_data = json.load(f)

            for template_id, data in custom_data.items():
                if template_id in self.templates:
                    default_template = self.templates[template_id]
                    self.templates[template_id] = Template.from_dict(
                        data, default_template
                    )
                    
        except Exception as e:
            logging.error(f"Error loading custom prompts: {e}")
            # Don't raise - continue with defaults