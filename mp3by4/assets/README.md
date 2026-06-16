# Assets Folder

Place your character images in subdirectories here.

## Structure

```
assets/
  character1/
    closed.png    # Character with closed mouth
    open.png      # Character with open mouth
  character2/
    closed.png
    open.png
  ...
```

## Image Requirements

- **Format**: PNG (supports transparency)
- **Recommended Size**: 1080x1920 (portrait) or 720x1280
- **Aspect Ratio**: Will be resized to fit video frame (1280x720)
- **Transparency**: Use alpha channel for better blending

## Usage

When making a request to `/process`, include the `character_name` parameter:

```json
{
  "content": "your text here",
  "character_name": "character1"
}
```

If `character_name` is not provided or the character folder doesn't exist, the system will fall back to geometric shapes.

