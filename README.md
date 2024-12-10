# PyGit: A Python Implementation of Git

PyGit is a lightweight implementation of Git's core functionality in Python, designed to help understand Git's internal workings. This project implements the fundamental concepts of version control including commits, branches, merging, and remote operations.

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

