FROM odoo:18.0

USER root

# Dev tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    vim \
    sudo \
    catdoc \
    && rm -rf /var/lib/apt/lists/*

# Thai fonts for PDF generation
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-thai-tlwg \
    && rm -rf /var/lib/apt/lists/*

# Allow odoo user to use sudo
RUN echo "odoo ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER odoo
