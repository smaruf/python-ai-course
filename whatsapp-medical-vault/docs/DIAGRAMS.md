# PlantUML Diagrams - Viewing Guide

This project includes 6 comprehensive PlantUML architecture diagrams. This guide explains how to view and edit them.

## 📊 Available Diagrams

1. **[System Architecture](diagrams/system-architecture.puml)** - Complete system overview with webhook/pub-sub and push-pull patterns
2. **[Component Diagram](diagrams/component-diagram.puml)** - Detailed component interactions using C4 model
3. **[Upload Flow Sequence](diagrams/sequence-upload-flow.puml)** - Step-by-step document upload process
4. **[Retrieval Flow Sequence](diagrams/sequence-retrieval-flow.puml)** - Document retrieval and command processing
5. **[Data Model](diagrams/data-model.puml)** - Complete database schema with relationships
6. **[Deployment Architecture](diagrams/deployment-architecture.puml)** - Cloud deployment on AWS/DigitalOcean

## 🔍 Viewing Options

### Option 1: VS Code Extension (Recommended)

1. **Install PlantUML Extension**:
   - Open VS Code
   - Go to Extensions (Ctrl+Shift+X / Cmd+Shift+X)
   - Search for "PlantUML"
   - Install "PlantUML" by jebbs

2. **Install Java** (required for PlantUML):
   ```bash
   # macOS
   brew install openjdk
   
   # Ubuntu/Debian
   sudo apt-get install default-jre
   
   # Windows
   # Download from https://www.oracle.com/java/technologies/downloads/
   ```

3. **Install Graphviz** (for diagram rendering):
   ```bash
   # macOS
   brew install graphviz
   
   # Ubuntu/Debian
   sudo apt-get install graphviz
   
   # Windows (using Chocolatey)
   choco install graphviz
   ```

4. **View Diagrams**:
   - Open any `.puml` file in VS Code
   - Press `Alt+D` (or `Option+D` on macOS) to preview
   - Or right-click and select "Preview Current Diagram"

5. **Export Diagrams**:
   - Right-click in the editor
   - Select "Export Current Diagram"
   - Choose format (PNG, SVG, PDF)

### Option 2: Online PlantUML Viewer

1. Visit [PlantUML Web Server](http://www.plantuml.com/plantuml/uml/)

2. Copy the content of any `.puml` file

3. Paste into the text area

4. Click "Submit" to generate the diagram

5. Download as PNG or SVG using the buttons at the top

### Option 3: PlantUML Command Line

1. **Install PlantUML**:
   ```bash
   # macOS
   brew install plantuml
   
   # Ubuntu/Debian
   sudo apt-get install plantuml
   
   # Or download JAR directly
   wget https://sourceforge.net/projects/plantuml/files/plantuml.jar/download -O plantuml.jar
   ```

2. **Generate diagrams**:
   ```bash
   # Single file
   plantuml docs/diagrams/system-architecture.puml
   
   # All diagrams
   plantuml docs/diagrams/*.puml
   
   # Specific format
   plantuml -tsvg docs/diagrams/system-architecture.puml
   plantuml -tpng docs/diagrams/*.puml
   ```

3. **Generated files** will be created in the same directory:
   - `system-architecture.png`
   - `component-diagram.png`
   - etc.

### Option 4: IntelliJ IDEA / PyCharm

1. **Install PlantUML Integration Plugin**:
   - Go to File → Settings → Plugins
   - Search for "PlantUML integration"
   - Install and restart

2. **View Diagrams**:
   - Open any `.puml` file
   - Diagram preview appears automatically
   - Can export to various formats

### Option 5: Browser Extensions

#### Chrome/Edge:
- Install "PlantUML Viewer" extension
- Open `.puml` files directly in browser
- Diagrams render automatically

#### Firefox:
- Install "PlantUML Renderer" add-on
- Similar functionality to Chrome extension

## 🎨 Editing Diagrams

### VS Code Setup
```json
// Add to settings.json for better experience
{
  "plantuml.server": "https://www.plantuml.com/plantuml",
  "plantuml.render": "PlantUMLServer",
  "plantuml.previewAutoUpdate": true,
  "plantuml.exportFormat": "png",
  "plantuml.exportSubFolder": false
}
```

### Useful PlantUML Resources

- **Official Documentation**: https://plantuml.com/
- **Sequence Diagrams**: https://plantuml.com/sequence-diagram
- **Component Diagrams**: https://plantuml.com/component-diagram
- **Class Diagrams**: https://plantuml.com/class-diagram
- **Deployment Diagrams**: https://plantuml.com/deployment-diagram
- **C4 Model**: https://github.com/plantuml-stdlib/C4-PlantUML

### Common PlantUML Commands

```plantuml
' Comments start with '

' Participants
participant "User" as User
database "Database" as DB

' Messages
User -> DB: Query
DB --> User: Result

' Activation
activate User
deactivate User

' Notes
note right of User
  This is a note
end note

' Colors
User -> DB #green: Success
User -> DB #red: Error

' Groups
group Authentication
  User -> DB: Login
end
```

## 🖼️ Generating Documentation

### Generate All Diagrams for Documentation

```bash
#!/bin/bash
# generate_diagrams.sh

cd docs/diagrams

# Generate PNG for README
plantuml -tpng *.puml

# Generate SVG for documentation
plantuml -tsvg *.puml

# Generate PDF for presentations
plantuml -tpdf *.puml

echo "✅ All diagrams generated!"
```

### Include in Markdown

```markdown
# System Architecture

![System Architecture](diagrams/system-architecture.png)

For detailed view, see [system-architecture.puml](diagrams/system-architecture.puml)
```

## 🔧 Troubleshooting

### Issue: "Cannot find Java"
**Solution**: Install Java JRE/JDK
```bash
java -version  # Check if installed
```

### Issue: "Cannot find Graphviz"
**Solution**: Install Graphviz
```bash
dot -version  # Check if installed
```

### Issue: "Syntax error in diagram"
**Solution**: Check PlantUML syntax
- Remove special characters
- Check matching parentheses/braces
- Validate against PlantUML online

### Issue: "Diagram too large"
**Solution**: Split into multiple diagrams or increase memory
```bash
plantuml -DPLANTUML_LIMIT_SIZE=8192 diagram.puml
```

### Issue: "Font rendering issues"
**Solution**: Install better fonts
```bash
# Ubuntu/Debian
sudo apt-get install fonts-dejavu fonts-liberation

# macOS
# Fonts are usually included
```

## 📝 Best Practices

1. **Keep diagrams focused** - One diagram, one concept
2. **Use consistent naming** - Follow a naming convention
3. **Add comments** - Explain complex parts
4. **Version control** - Keep `.puml` files in Git
5. **Generate on build** - Automate diagram generation
6. **Export for sharing** - PNG/SVG for non-technical stakeholders

## 🚀 Advanced: CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Generate PlantUML Diagrams

on:
  push:
    paths:
      - 'docs/diagrams/*.puml'

jobs:
  generate-diagrams:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install PlantUML
        run: |
          sudo apt-get update
          sudo apt-get install -y plantuml graphviz
      
      - name: Generate diagrams
        run: |
          cd docs/diagrams
          plantuml -tpng *.puml
          plantuml -tsvg *.puml
      
      - name: Commit generated diagrams
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add docs/diagrams/*.png docs/diagrams/*.svg
          git commit -m "Auto-generate PlantUML diagrams" || echo "No changes"
          git push
```

## 📚 Additional Resources

- **PlantUML Cheat Sheet**: https://ogom.github.io/draw_uml/plantuml/
- **Real-World Examples**: https://real-world-plantuml.com/
- **PlantUML Themes**: https://github.com/plantuml/plantuml/tree/master/themes
- **C4 Model Examples**: https://github.com/plantuml-stdlib/C4-PlantUML/tree/master/samples

---

For questions or issues with diagrams, please open an issue in the repository.
