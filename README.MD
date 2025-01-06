# Markdown File Sorter

This Python program sorts and manages Markdown files in a specified directory based on a `sort:` value inside each file.

## Example
```
  0.0 Lego Star Wars - The Skywalker Saga (2021).md
  10.0 Heaven Will Be Mine (2018).md
  20.0 Deception III - Dark Delusion (1999).md
  30.0 Xenoblade Chronicles 3 Future Redeemed.md
  40.0 Mario Bros Wonder.md
```

## Requirements
- Python 3.x
- `curses` library (pre-installed on Linux/macOS)

## Usage
1. Set `DIRECTORY` to your target folder.
2. Run the script:  
   ```bash
   python3 markdown_sorter.py
   ```
3. Controls:
   - **Up/Down Arrows**: Navigate
   - **','**: Previous page
   - **'.'**: Next page
   - **Enter**: Move file
   - **'i'**: Input sort value
   - **'a'**: Resort all files
   - **'q'**: Quit

## License
MIT License
