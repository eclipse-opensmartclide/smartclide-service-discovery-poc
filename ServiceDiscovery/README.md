# Service Discovery - SmartCLIDE
Eclipse Public License 2.0

# Configure 
This package relies on tokens from GitGub, GitLab and BitBucket APIs that are configured in the config.ini file in the root of the service.
The service also depends on an instance of Elasticsearch to store and collect information, where the configuration of the IP, port and credentials are done in this same file.
    See: https://github.com/eclipse-researchlabs/smartclide-service-discovery-poc/blob/main/ServiceDiscovery/config.ini

The service makes use of the 2020 port, be sure to expose it.

# Build
```
    python3 -m pip install --no-cache-dir -r requirements.txt
    python3 -m pip install . --upgrade
```
# Run
```
python3 servicediscovery
```