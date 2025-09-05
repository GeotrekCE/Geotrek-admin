# Geotrek-admin Development Instructions

Geotrek-admin is a Django-based geospatial web application for managing trekking, outdoor tourism data and geographic information. It uses PostGIS for spatial data, Redis for caching, and provides both a web admin interface and comprehensive APIs.

**Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Working Effectively

### Network Limitations - CRITICAL
- **Docker build from source FAILS** due to firewall limitations preventing Python download from GitHub
- Timeout occurs when downloading `cpython-3.10.18+20250828-x86_64-unknown-linux-gnu-install_only_stripped.tar.gz`
- Build fails after exactly ~2 minutes with "operation timed out" error
- **WORKAROUND**: Use pre-built official images: `docker pull geotrekce/admin:latest`
- **Do not attempt** `docker compose build` - it will fail after ~2 minutes with network timeout
- **Alternative**: Use Ubuntu package installation method for full functionality

### Development Setup (Network-Limited Environment)
Use these **validated commands** in order:

```bash
# 1. Setup environment and permissions
cp .env.dist .env
mkdir -p var/{log,cache,media,static,tmp,conf}
chmod -R 777 var
echo "127.0.0.1 geotrek.local" | sudo tee -a /etc/hosts

# 2. Pull pre-built image and tag for local use
docker pull geotrekce/admin:latest
docker tag geotrekce/admin:latest geotrek:latest

# 3. Start services (supporting containers work fine)
docker compose up postgres redis convertit screamshotter -d
# Wait for postgres to be healthy (about 30 seconds)

# 4. Note: Full development environment setup currently blocked by network limitations
# Web container cannot start properly due to missing development dependencies in production image
```

**TIMING**: Service startup takes ~30-45 seconds. NEVER CANCEL during startup phase.

### Alternative Installation Methods
For full functionality, use one of these alternatives:

1. **Ubuntu Package Installation** (Recommended for production-like setup):
   ```bash
   # Follow instructions from docs/installation-and-configuration/installation.rst
   bash -c "$(curl -fsSL https://raw.githubusercontent.com/GeotrekCE/Geotrek-admin/master/tools/install.sh)"
   ```

2. **Manual Dependencies Setup** (If Docker build works in your environment):
   ```bash
   # Only try if network allows GitHub downloads
   docker compose build  # Takes 5-10+ minutes, often fails
   docker compose run --rm web update.sh  # Takes 2-5 minutes
   docker compose run --rm web load_data.sh  # Takes 5-15 minutes
   ```

## Testing

### Django Tests
**CRITICAL TIMING**: Django tests take 15-30+ minutes. **NEVER CANCEL.** Set timeout to 45+ minutes minimum.

```bash
# Full test suite with coverage (LONG RUNNING - 20-30 minutes)
make coverage  # NEVER CANCEL: Takes 20-30 minutes. Set timeout to 45+ minutes

# Specific test environments  
make test      # NEVER CANCEL: Standard tests, ~15 minutes, set timeout to 30+ minutes
make test_nds  # NEVER CANCEL: Non-dynamic segmentation tests, ~15 minutes, set timeout to 30+ minutes  
make tests     # NEVER CANCEL: Both test and test_nds, ~30 minutes, set timeout to 60+ minutes
```

**Note**: Tests require fully built development environment, which may not work due to network limitations documented above.

### Code Quality (Requires Development Environment)
```bash
make quality   # ❌ Currently fails: ruff not found in production image
make lint      # ❌ Currently fails: ruff not found in production image  
make format    # ❌ Currently fails: ruff not found in production image
```

**Note**: Quality commands require development environment with ruff installed. Use alternative installation method for full functionality.

### End-to-End Tests (Cypress)
**CRITICAL**: Requires complete setup with loaded data. Takes 10-15 minutes. **NEVER CANCEL.**

```bash
# Setup test data first (NEVER CANCEL each step)
make load_data              # NEVER CANCEL: ~5-10 minutes, set timeout to 20+ minutes
make load_test_integration  # NEVER CANCEL: ~2-5 minutes, set timeout to 15+ minutes

# Run Cypress tests (NEVER CANCEL)
cd cypress
npm ci                      # NEVER CANCEL: ~2-3 minutes first time, set timeout to 10+ minutes
./node_modules/.bin/cypress run  # NEVER CANCEL: ~5-10 minutes, set timeout to 20+ minutes
```

**Warning**: These commands require working development environment setup.

## Key Development Commands

### Management Commands (After successful setup)
```bash
# Database operations
docker compose run --rm web ./manage.py migrate
docker compose run --rm web ./manage.py createsuperuser
docker compose run --rm web ./manage.py collectstatic --clear --noinput

# Translations
make messages           # Extract translatable strings
make compilemessages   # Compile translations

# Dependencies (requires network access)
make deps              # Update all requirements files, ~2-3 minutes
```

### Running the Application
```bash
# Development server (if working environment)
docker compose up  # Access at http://geotrek.local:8000
# or
make serve
```

## Validation Scenarios

**Always test these workflows after making changes:**

### 1. Basic Django Functionality
```bash
# Verify Django starts without errors
docker compose run --rm web ./manage.py check

# Test basic management commands  
docker compose run --rm web ./manage.py help
```

### 2. Database Operations
```bash
# Test database connectivity
docker compose run --rm web ./manage.py dbshell -c "SELECT version();"

# Verify migrations
docker compose run --rm web ./manage.py showmigrations
```

### 3. API Endpoint Testing
```bash
# Test API availability (if server running)
curl -f http://geotrek.local:8000/api/settings.json
```

## What Actually Works in Network-Limited Environments

### ✅ Verified Working Commands
```bash
# Service management
docker compose up postgres redis convertit screamshotter -d
docker compose down
docker compose ps

# Image management  
docker pull geotrekce/admin:latest
docker tag geotrekce/admin:latest geotrek:latest

# File system operations
cp .env.dist .env
mkdir -p var/{log,cache,media,static,tmp,conf}
chmod -R 777 var

# Basic validation
curl -I https://raw.githubusercontent.com/GeotrekCE/Geotrek-admin/master/tools/install.sh
```

### ❌ Known Failing Commands
```bash
# Development environment setup
docker compose build                    # Network timeout
docker compose run --rm web update.sh   # Missing dependencies  
make test                               # Requires dev environment
make lint                               # Missing ruff in production image
```

### 🔄 Recommended Workflow for Coding Agents

1. **Always start with what works**: Pull official images and set up supporting services
2. **Document network limitations** clearly in any changes
3. **Use Ubuntu package installation** for full development environment
4. **Focus on file-based changes** that don't require running the full application
5. **Test with alternative installation methods** when full validation is needed

## Verified Command Timings

**Based on actual testing - use these timeout values:**

| Command | Duration | Recommended Timeout | Status |
|---------|----------|-------------------|---------|
| `docker compose build` | ~2 minutes | ❌ FAILS | Network timeout |
| `docker compose up postgres` | ~30 seconds | 120 seconds | ✅ Works |
| `docker pull geotrekce/admin:latest` | ~2-3 minutes | 600 seconds | ✅ Works |
| `make quality` | ~30 seconds | 120 seconds | ❌ Missing ruff |
| `make lint` | ~15 seconds | 60 seconds | ❌ Missing ruff |
| `make format` | ~10 seconds | 60 seconds | ❌ Missing ruff |
| `make test` | ~15+ minutes | 1800+ seconds | ❌ Needs dev env |
| `make coverage` | ~20-30 minutes | 2700+ seconds | ❌ Needs dev env |
| Cypress tests | ~10-15 minutes | 1200+ seconds | ❌ Needs dev env |

**Key**: ✅ = Verified working, ❌ = Known to fail or missing dependencies

## Common Tasks

### Repository Structure
```
/home/runner/work/Geotrek-admin/Geotrek-admin/
├── geotrek/           # Main Django application
│   ├── settings/      # Django settings
│   ├── api/          # REST API
│   ├── trekking/     # Core trekking models
│   ├── tourism/      # Tourism models  
│   └── ...           # Other Django apps
├── docker/           # Docker configuration
├── docs/             # Sphinx documentation
├── cypress/          # E2E tests
├── requirements.txt  # Python dependencies
├── Makefile         # Build shortcuts
└── docker-compose.yml
```

### Key Files to Monitor
- `geotrek/settings/` - Django configuration
- `requirements.txt` / `requirements-dev.txt` - Dependencies
- `Makefile` - Build and test commands
- `.env` - Environment configuration
- `docker-compose.yml` - Service definitions

### Configuration Files
- `ruff.toml` - Code quality configuration
- `setup.py` - Package definition and dependencies
- `.env.dist` - Environment template

## Troubleshooting

### Known Issues
1. **Docker build fails**: Use pre-built images as documented above
2. **Permission errors**: Ensure `var/` directory has proper permissions (777)
3. **Network timeouts**: All downloads from GitHub may fail in restricted environments
4. **Database connection**: Ensure PostgreSQL container is healthy before running commands

### Log Locations
- Application logs: `var/log/`
- Docker logs: `docker compose logs [service]`
- Test results: Console output, Cypress videos in `cypress/videos/`

### Performance Notes
- Database queries can be slow due to complex geometric operations
- PDF generation requires proper domain setup (geotrek.local)
- Map tiles and static files need proper permissions

## CI/CD Integration

The repository includes GitHub Actions workflows:
- `.github/workflows/test.yml` - Comprehensive test matrix
- `.github/workflows/lint.yml` - Code quality checks
- `.github/workflows/doc.yml` - Documentation builds

**Always run** `make quality` before committing to match CI requirements.

## Required System Resources
- 4+ CPU cores (for complex geometric operations)
- 8+ GB RAM (PostGIS operations are memory-intensive)  
- 50+ GB disk space (including media files)
- Docker with at least 4GB memory allocation

## Important Notes
- **NEVER CANCEL** long-running operations (builds, tests) - they may take 30+ minutes
- Always use timeout values of 45+ minutes for build operations
- Always use timeout values of 30+ minutes for test operations
- Always validate changes with both Django and Cypress tests when possible
- Geographic operations are CPU-bound and take significant time
- The application serves as the backend for Geotrek-rando (public website) and Geotrek-mobile apps