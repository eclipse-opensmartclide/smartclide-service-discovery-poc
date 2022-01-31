# Service Discovery API - SmartCLIDE
Maintainer:  AIR Institute

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


# Web service listings - SmartCLIDE
Maintainer:  AIR Institute

# Run
This script collects information from Programableweb, to avoid saturation and blocking of IP addresses by a high number of requests, this script can be executed on a regular basis, obtaining a section each time.

When launched, information is collected in batches that are exported to .csv files, and when a batch is finished, the results are merged under the same .csv file.