# smartclide-service-discovery-poc
Uses port 2020

# Configure
This package relies on tokens from GitGub, GitLab and BitBucket APIs that are embedded in the python package for security.

See: https://github.com/eclipse-researchlabs/smartclide-service-discovery-poc/blob/main/ServiceDiscovery/servicediscovery/config.py

# Build
```
    python3 -m pip install --no-cache-dir -r requirements.txt
    python3 -m pip install . --upgrade
```
# Run
```
python3 servicediscovery
```
