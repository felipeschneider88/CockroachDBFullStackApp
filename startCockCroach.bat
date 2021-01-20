cd /
cd cockroach
Rem start insecure instance, uncomment the line belove this one
Rem .\cockroach.exe start-single-node --insecure --listen-addr=localhost:26257 --http-addr=localhost:8080 

Rem start secure instance
.\cockroach.exe start-single-node --listen-addr=localhost:26257 --http-addr=localhost:8080 --certs-dir=certs
