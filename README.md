# PyGit

PyGit is a lightweight implementation of Git's core functionality in Python, designed to help understand Git's internal workings.

## Features

PyGit provides a comprehensive set of Git-like commands with core version control functionality:

- Basic Commands: `init`, `add`, `commit`, `status`, `log`, `checkout`, `clone`
- Branch Operations: Create, list, and switch branches
- Remote Operations: `fetch`, `push`
- Low-level Commands: `hash-object`, `cat-file`, `write-tree`, `read-tree`

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

3. Install the package in editable mode:
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
pygit add hello.txt
pygit commit -m "Initial commit"

# Check status and history
pygit status
pygit log
```

### Branching and Merging

```bash
# Create and switch to a new branch
pygit branch feature-branch
pygit checkout feature-branch

# Make changes and commit
echo "New feature" > feature.txt
pygit add feature.txt
pygit commit -m "Add new feature"

# Merge back to master
pygit checkout master
pygit merge feature-branch
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
├── .pygit/           # Repository metadata
│   ├── objects/     # Object storage
│   └── refs/        # References (branches, tags)
├── pygit/            # Python source code
│   ├── base.py
│   ├── cli.py
│   ├── data.py
│   ├── diff.py
│   └── remote.py
├── tests/           # Python test suite
│   ├── test_base.py
│   ├── test_data.py
│   └── test_remote.py
└── README.md
```

## Running Tests

```bash
# Navigate to tests directory
cd tests

# Run test suite
python -m unittest discover
```

## Comparison with Conventional Git

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

