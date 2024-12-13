# Video Narrator Pro

A professional tool for generating natural-sounding narration scripts from video content using GPT-4 Vision analysis.

## Features

- Video frame analysis using GPT-4 Vision API
- Natural language narration generation
- Customizable narration templates
- Clean output suitable for text-to-speech systems
- Professional GUI interface
- Progress tracking and error handling
- Separate timing data for video synchronization

## Requirements

- Python 3.8+
- OpenAI API key with GPT-4 Vision access
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/red4golf/video-narrator-pro.git
cd video-narrator-pro
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a .env file with your OpenAI API key:
```
OPENAI_API_KEY=your-api-key-here
```

## Usage

1. Run the application:
```bash
python run.py
```

2. Select a template for your video type
3. Choose your video file
4. Start the analysis process
5. Generate a natural narration script
6. Use the output with your preferred text-to-speech system

## Templates

- Room Walk-through: Ideal for real estate and interior tours
- Outdoor Scenes: Perfect for landscapes and exterior views
- Event Coverage: Suited for ceremonies and gatherings
- Product Showcase: Designed for product demonstrations

## Output Files

The system generates two files for each narration:
- `*_narration.txt`: Clean narration text ready for TTS
- `*_timing.json`: Technical timing data for synchronization

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)