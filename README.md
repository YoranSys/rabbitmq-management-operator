# rabbitmq-management-operator




# Install
Create a values.yaml file containing rabbitMQ configuration

```yaml
rabbitmq:
  user: "user"
  password: "MyPassword"
  # Management API url
  managementUrl: "http://rabbitmq.default.svc.cluster.local:15672"
  # If needed Verify TLS certificat validity
  verify: 'False'
```

# Install the operator

```bash
helm upgrade -i rabbitmq-operator ./helm/rabbitmq-management-operator -f ./values.yaml
```

# Test

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name:  mynamespace
  
---

kind: RabbitMQUser
apiVersion: kopf.dev/v1
metadata:
  name: MyUserAndVhost
  namespace: mynamespace
spec:
  username: myuser1
  password:
    key: password
    name: mysecret
  vhost: vhost1
  tags: vhost1,management

---

apiVersion: v1
kind: Secret
metadata:
  name: mysecret
  namespace: mynamespace
type: Opaque
data:
  password: TXlQYXNzd29yZA==
```

# Developement 

Based on kopf framework

```bash
kopf run rabbitmq-management.py --verbose
```

docker build . -t yoransys/rabbitmq-management-operator:0.1.0