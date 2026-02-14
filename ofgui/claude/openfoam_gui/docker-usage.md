# Using OpenFOAM GUI with Docker

## Quick Start

### 1. Build Image

```bash
docker-compose build
```

### 2. Run Container

```bash
# On Linux
xhost +local:docker  # Allow Docker to access X server
docker-compose up -d

# On macOS (requires XQuartz)
open -a XQuartz
xhost + localhost
docker-compose up -d

# On Windows WSL2
# Install VcXsrv or Xming
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
docker-compose up -d
```

### 3. Access GUI

The OpenFOAM GUI will launch automatically.

## Docker Commands

### Build

```bash
# Build image
docker-compose build

# Build without cache
docker-compose build --no-cache
```

### Run

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Execute Commands

```bash
# Open bash shell in container
docker-compose exec openfoam-gui bash

# Run specific case
docker-compose exec openfoam-gui bash -c "cd cases/cavity && blockMesh && icoFoam"

# Run tests
docker-compose exec openfoam-gui bash -c "cd openfoam_gui && ./run_tests.sh"
```

## Volumes

### Cases Directory

The `./cases` directory is mounted to `/home/openfoam/cases` in the container.

```bash
# Create case on host
mkdir -p cases/myCase

# Access in container
docker-compose exec openfoam-gui bash
cd /home/openfoam/cases/myCase
```

### Configuration

User configuration is mounted from `~/.openfoam_gui`.

## ParaView Integration

Launch ParaView for visualization:

```bash
docker-compose --profile paraview up paraview
```

## Troubleshooting

### Display Issues

```bash
# Check DISPLAY variable
echo $DISPLAY

# Allow X11 access
xhost +local:docker

# Test X11
docker-compose exec openfoam-gui xeyes
```

### Permission Issues

```bash
# Fix file permissions
docker-compose exec openfoam-gui sudo chown -R openfoam:openfoam /home/openfoam/cases
```

### GPU Access

For hardware acceleration:

```bash
# Check GPU devices
ls -la /dev/dri

# Add to docker-compose.yml
devices:
  - /dev/dri:/dev/dri
```

## Production Deployment

For production use:

1. Use specific version tags
2. Set resource limits
3. Configure logging
4. Enable auto-restart
5. Use Docker secrets for sensitive data

## Clean Up

```bash
# Stop and remove containers
docker-compose down

# Remove volumes
docker-compose down -v

# Remove images
docker rmi openfoam-gui:latest
```
