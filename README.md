# PyGit: A Python Implementation of Git

PyGit is a lightweight implementation of Git's core functionality in Python. This project implements the fundamental concepts of version control including commits, branches, merging, and remote operations.

## Features

- **Basic Version Control**
  - Initialize repositories (`init`)
  - Stage changes (`add`)
  - Create commits (`commit`)
  - View status (`status`)
  - View history (`log`)

- **Branch Management**
  - Create branches (`branch`)
  - Switch branches (`checkout`)
  - Merge branches (`merge`)
  - View branch structure (`k`)

- **Remote Operations**
  - Clone repositories (`clone`)
  - Fetch changes (`fetch`)
  - Push changes (`push`)

- **Low-level Operations**
  - Hash objects (`hash-object`)
  - View object contents (`cat-file`)
  - Manipulate trees (`write-tree`, `read-tree`)

## Requirements

1. Python 3.6 or higher
2. Graphviz (for visualization features)
   - Windows: Download from https://graphviz.org/download/
   - Linux: `sudo apt-get install graphviz`
   - macOS: `brew install graphviz`

## Installation

1. Install Graphviz (see Requirements above)

2. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pygit.git
   cd pygit
   ```

2. Install in development mode:
   ```bash
   pip install -e .
   ```

4. Verify installation:
   ```bash
   pygit --help
   ```

## Usage Examples

### Basic Workflow

Initialize a repository:
```bash
# Create project directory
mkdir my-project
cd my-project

# Initialize repository
pygit init

# Create and add files
echo "Hello, PyGit!" > hello.txt
pygit add hello.txt or pygit add .
pygit commit -m "Initial commit"

# View status and history
pygit status
pygit log
```

### Branch Operations

```bash
# Create and switch branches
pygit branch feature
pygit checkout feature

# Make changes
echo "New feature" > feature.txt
pygit add feature.txt
pygit commit -m "Add feature"

# Merge changes
pygit checkout master
pygit merge feature
```

### Remote Operations

```bash
# Clone a repository
pygit clone /path/to/source/repo /path/to/destination

# Fetch and push
pygit fetch /path/to/remote
pygit push /path/to/remote master
```

## Project Structure

```
pygit/
├── __init__.py
├── base.py      # Core VCS functionality
├── cli.py       # Command-line interface
├── commands.py  # Command implementations
├── data.py      # Data storage operations
├── diff.py      # Diff and merge logic
├── parser.py    # Command parsing
└── remote.py    # Remote operations
```

## Implementation Details

### Object Storage
- Objects are stored in `.pygit/objects/` using SHA-1 hashes
- Supports blobs (files), trees (directories), and commits

### Index Management
- Staging area implemented in `.pygit/index`
- JSON format for simplicity

### Branch Management
- Branches stored in `.pygit/refs/heads/`
- HEAD reference tracks current branch

### Similarities

#### Content-Addressable Storage
Both PyGit and Git use SHA-1 hash algorithms to store objects, creating a unique identifier for each piece of content. This approach ensures data integrity and allows for efficient content retrieval. In both systems, objects are stored based on their content hash, which means identical files will always have the same hash, regardless of their location or when they were created.

#### References Management
Both implementations use a reference system to manage branches, tags, and the current state of the repository. References are essentially pointers to specific commits, allowing for easy navigation and tracking of the repository's history. This includes maintaining HEAD references, branch pointers, and the ability to create and switch between different references.

#### Commit Graph Structure
PyGit and Git both represent the repository's history as a directed acyclic graph (DAG) of commits. Each commit points to its parent commit(s), creating a linear or branching history. This structure allows for tracking changes, understanding the evolution of the project, and supporting branching and merging operations.

### Key Differences

#### Simplified Model
Unlike Git, which offers a comprehensive set of version control features, PyGit is a minimalist implementation focused on core functionality. Git provides advanced features like:
- Interactive rebasing
- Stashing changes
- Sophisticated conflict resolution
- Submodule management
- Extensive branching strategies

PyGit strips away these complex features to provide a lightweight implementation that demonstrates the fundamental principles of version control.

#### Single Remote Support
Git supports multiple named remotes with complex remote management capabilities, including:
- Multiple remote repositories
- Different push and fetch URLs
- Advanced remote tracking
- Detailed remote branch management

In contrast, PyGit offers basic remote operations with limited remote management. It provides a simplified approach to working with remote repositories, focusing on the core concepts of fetching and pushing changes.

#### No Packfile Compression
Git uses a sophisticated packfile system for:
- Compressing repository data
- Reducing storage space
- Improving network transfer efficiency
- Handling large repositories with many objects

PyGit stores objects as loose files without advanced compression techniques. This approach:
- Simplifies the implementation
- Increases storage requirements
- Reduces performance for large repositories
- Makes the internal storage mechanism more transparent and easier to understand

#### Basic Merging Strategies
Git offers advanced merge capabilities:
- Automatic conflict detection
- Multiple merge strategies (recursive, octopus, etc.)
- Interactive merge conflict resolution
- Detailed conflict marking

PyGit implements only basic merging:
- Simple linear merge attempts
- Limited conflict handling
- Requires manual intervention for complex merge scenarios
- Focuses on demonstrating the fundamental merge concept

## Ignoring Files

PyGit uses `.pygitignore` files to determine which files and directories to ignore. Only the `.pygit/` directory is ignored by default.

### Creating a .pygitignore File

Create a `.pygitignore` file in your repository root:
```bash
# Create .pygitignore
touch .pygitignore

# Add patterns to ignore
echo "*.log" >> .pygitignore
echo "node_modules/" >> .pygitignore
```

### Ignore Patterns

The `.pygitignore` file supports several pattern formats:

1. **Directory patterns** (ending with `/`):
   ```
   node_modules/    # Ignores the entire directory
   build/          # Ignores build directory
   ```

2. **File patterns with wildcards** (`*`):
   ```
   *.log           # Ignores all .log files
   *.pyc           # Ignores Python compiled files
   test_*.py       # Ignores test files
   ```

3. **Exact matches**:
   ```
   secret.txt      # Ignores specific file
   config.json     # Ignores specific file
   ```

4. **Comments and formatting**:
   ```
   # This is a comment
   
   # Python files
   *.pyc
   __pycache__/
   
   # Build directories
   dist/
   build/
   ```

### Example .pygitignore

```
# Development
__pycache__/
*.pyc
*.pyo
.env

# Dependencies
node_modules/
venv/
.venv/

# Build outputs
dist/
build/
*.egg-info/

# Logs and databases
*.log
*.sqlite

# IDE specific
.vscode/
.idea/
*.swp
```

Note: Unlike Git, PyGit only ignores files that are explicitly listed in `.pygitignore` (except for the `.pygit/` directory which is always ignored).

## Testing

PyGit includes a comprehensive test suite covering core functionality. The tests are located in the `test/` directory.

### Test Structure
```
test/
├── __init__.py
├── run_tests.py          # Test runner script
├── test_base.py          # Core operations tests
├── test_branch.py        # Branch operations tests
├── test_data.py          # Data storage tests
├── test_diff.py          # Diff functionality tests
├── test_ignore.py        # Ignore pattern tests
├── test_remote.py        # Remote operations tests
└── test_status.py        # Status reporting tests
```

### Running Tests

There are several ways to run the tests:

1. Using the test runner script (recommended):
```bash
# From project root directory
python -m test.run_tests

# Or from test directory
cd test
python run_tests.py
```

2. Using Python's unittest directly:
```bash
# Run all tests
python -m unittest discover test

# Run specific test file
python -m unittest test.test_base
python -m unittest test.test_branch
```

3. Using pytest (optional):
```bash
# Install pytest first
pip install pytest

# Run all tests
pytest test/

# Run specific test file
pytest test/test_base.py
```

### Test Coverage

The test suite covers:
- Basic operations (init, add, commit)
- Branch management (create, checkout, switch)
- Remote operations (clone, fetch, push)
- Data storage (objects, refs, index)
- Diff functionality
- Ignore patterns
- Status reporting
- Working directory operations

### Running Tests During Development

Before running tests:
1. Ensure you're in your virtual environment (if using one)
2. Install the package in development mode:
```bash
pip install -e .
```

Test output will show:
- Number of tests run
- Test results (pass/fail)
- Any errors or failures
- Test execution time

### Adding New Tests

When adding new features, corresponding tests should be added to maintain code quality. Tests should:
- Be placed in the appropriate test file
- Follow the existing naming convention (test_*.py)
- Include clear docstrings explaining the test purpose
- Cover both success and failure cases

