# OpenFOAM GUI Docker Image
FROM ubuntu:22.04

LABEL maintainer="openfoam-gui@example.com"
LABEL description="OpenFOAM GUI - Star-CCM+ style interface"

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    python3-venv \
    python3-dev \
    libgl1-mesa-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    qt6-base-dev \
    libqt6gui6 \
    libqt6widgets6 \
    build-essential \
    git \
    wget \
    sudo \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# Install OpenFOAM (example for OpenFOAM.org version)
RUN wget -q -O - https://dl.openfoam.org/gpg.key | apt-key add - && \
    echo "deb https://dl.openfoam.org/ubuntu focal main" > /etc/apt/sources.list.d/openfoam.list && \
    apt-get update && \
    apt-get install -y openfoam2506 && \
    rm -rf /var/lib/apt/lists/*

# Set up OpenFOAM environment
RUN echo "source /opt/openfoam2506/etc/bashrc" >> /etc/bash.bashrc

# Create application user
RUN useradd -m -s /bin/bash openfoam && \
    echo "openfoam ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER openfoam
WORKDIR /home/openfoam

# Copy application files
COPY --chown=openfoam:openfoam . /home/openfoam/openfoam_gui

# Create virtual environment and install dependencies
RUN cd openfoam_gui && \
    python3 -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -e .

# Set up display for GUI
ENV DISPLAY=:0
ENV QT_X11_NO_MITSHM=1

# Create startup script
RUN echo '#!/bin/bash' > /home/openfoam/start-gui.sh && \
    echo 'cd /home/openfoam/openfoam_gui' >> /home/openfoam/start-gui.sh && \
    echo 'source venv/bin/activate' >> /home/openfoam/start-gui.sh && \
    echo 'source /opt/openfoam2506/etc/bashrc' >> /home/openfoam/start-gui.sh && \
    echo 'python main.py "$@"' >> /home/openfoam/start-gui.sh && \
    chmod +x /home/openfoam/start-gui.sh

# Expose ports (if needed for web interface in future)
EXPOSE 8080

# Default command
CMD ["/home/openfoam/start-gui.sh"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD pgrep -f "python.*main.py" > /dev/null || exit 1
