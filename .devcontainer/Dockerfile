FROM homeassistant/home-assistant

WORKDIR /workspaces

# Install Python dependencies from requirements
COPY requirements.txt ./
RUN pip3 install -r requirements.txt \
   && rm -rf requirements.txt

# Set the default shell to bash instead of sh
ENV SHELL /bin/bash