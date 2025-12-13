---
title: "Deployment Guide for Institutional Setups"
sidebar_label: "Institutional Deployment"
sidebar_position: 110
---

# Deployment Guide for Institutional Setups

## Overview

This guide provides comprehensive deployment instructions for the Physical AI & Humanoid Robotics course across different institutional environments. From small academic departments to large universities with complex IT infrastructures, this guide covers various deployment scenarios and best practices.

## Deployment Architectures

### 1. On-Premises Deployment

#### Single Server Setup
For small institutions or pilot programs with limited resources.

**Requirements:**
- **Server**: 16+ cores, 64GB+ RAM, 1TB+ SSD storage
- **OS**: Ubuntu 22.04 LTS or CentOS Stream 9
- **Network**: Gigabit Ethernet, firewall configuration
- **Storage**: NFS mount for shared data (optional)

**Installation Steps:**
```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Docker and Docker Compose
sudo apt install docker.io docker-compose-v2
sudo usermod -aG docker $USER

# 3. Install ROS 2 Humble Hawksbill
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update
sudo apt install curl gnupg lsb-release
curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | sudo gpg --dearmor -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
sudo apt update
sudo apt install ros-humble-desktop
sudo apt install python3-rosdep python3-rosinstall python3-rosinstall-generator python3-vcstool build-essential

# 4. Clone course repository
git clone https://github.com/institution/robotics-course.git
cd robotics-course

# 5. Configure environment
cp .env.example .env
# Edit .env with appropriate settings

# 6. Start services with Docker Compose
docker-compose -f docker-compose.onprem.yml up -d
```

**Docker Compose Configuration (docker-compose.onprem.yml):**
```yaml
version: '3.8'

services:
  # Course platform backend
  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    environment:
      - DB_HOST=postgres
      - REDIS_URL=redis://redis:6379
      - ROS_DOMAIN_ID=42
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    volumes:
      - ./data:/app/data

  # Frontend application
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000

  # Database
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: robotics_course
      POSTGRES_USER: course_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # Redis for caching and sessions
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

  # ROS 2 bridge
  ros-bridge:
    image: osrf/ros2-bridge:latest
    environment:
      - ROS_DOMAIN_ID=42
    network_mode: host  # For ROS 2 communication
    volumes:
      - /tmp/.X11-unix:/tmp/.X11-unix:rw

  # Gazebo simulation
  gazebo:
    image: osrf/gazebo:gz-harmonic
    environment:
      - DISPLAY=${DISPLAY}
    volumes:
      - /tmp/.X11-unix:/tmp/.X11-unix:rw
      - ./models:/root/.gazebo/models
    ports:
      - "11345:11345/udp"

volumes:
  postgres_data:
  redis_data:
```

#### Multi-Server Setup
For larger institutions with dedicated infrastructure.

**Architecture:**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │────│  API Servers    │────│   Database      │
│   (Nginx)       │    │  (Multiple)     │    │   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                    ┌─────────────────┐
                    │  Frontend       │
                    │  (React/Static) │
                    └─────────────────┘
```

**Installation Steps:**
```bash
# 1. Set up load balancer server
sudo apt install nginx haproxy

# Configure nginx load balancer (nginx.conf)
upstream api_servers {
    server api1.example.edu:8000 weight=1;
    server api2.example.edu:8000 weight=1;
    server api3.example.edu:8000 weight=1;
}

server {
    listen 80;
    server_name robotics.example.edu;

    location /api/ {
        proxy_pass http://api_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://frontend_server;
    }
}

# 2. Set up API servers (run on each API server)
# Use the same Docker Compose but without frontend and with external database
docker-compose -f docker-compose.api.yml up -d

# 3. Set up database server
# Install PostgreSQL with replication
sudo apt install postgresql-15 postgresql-contrib-15

# Configure replication and backup
# (Implementation specific to your needs)
```

### 2. Cloud-Based Deployment

#### AWS Deployment

**Infrastructure as Code (Terraform):**
```hcl
# main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC
resource "aws_vpc" "robotics_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "robotics-course-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "robotics_igw" {
  vpc_id = aws_vpc.robotics_vpc.id

  tags = {
    Name = "robotics-igw"
  }
}

# Public Subnets
resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.robotics_vpc.id
  cidr_block              = "10.0.${count.index}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "public-subnet-${count.index}"
  }
}

# Private Subnets
resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.robotics_vpc.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "private-subnet-${count.index}"
  }
}

# RDS Database
resource "aws_db_instance" "robotics_db" {
  identifier = "robotics-course-db"

  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.t3.medium"

  name     = "robotics_course"
  username = var.db_username
  password = var.db_password

  db_subnet_group_name = aws_db_subnet_group.robotics_db_subnet_group.name
  vpc_security_group_ids = [aws_security_group.db_sg.id]

  allocated_storage    = 100
  max_allocated_storage = 500
  storage_type         = "gp2"
  storage_encrypted    = true

  backup_retention_period = 7
  skip_final_snapshot     = false
  final_snapshot_identifier = "robotics-course-final-snapshot"

  tags = {
    Name = "robotics-db"
  }
}

# EKS Cluster
resource "aws_eks_cluster" "robotics_cluster" {
  name     = "robotics-course-cluster"
  role_arn = aws_iam_role.robotics_cluster_role.arn
  version  = "1.27"

  vpc_config {
    subnet_ids = concat(aws_subnet.public[*].id, aws_subnet.private[*].id)
  }

  depends_on = [
    aws_iam_role_policy_attachment.robotics_cluster_policy,
  ]
}

# ECR Repository for Docker images
resource "aws_ecr_repository" "robotics_app" {
  name                 = "robotics-course-app"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# Security Groups
resource "aws_security_group" "api_sg" {
  name_prefix = "robotics-api"
  vpc_id      = aws_vpc.robotics_vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "db_username" {
  description = "Database username"
  type        = string
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

# Data sources
data "aws_availability_zones" "available" {}
```

**Kubernetes Deployment (EKS):**
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: robotics-api
  namespace: robotics-course
spec:
  replicas: 3
  selector:
    matchLabels:
      app: robotics-api
  template:
    metadata:
      labels:
        app: robotics-api
    spec:
      containers:
      - name: api
        image: your-registry/robotics-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DB_HOST
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: host
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: password
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: robotics-api-service
  namespace: robotics-course
spec:
  selector:
    app: robotics-api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: robotics-ingress
  namespace: robotics-course
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - robotics.your-institution.edu
    secretName: robotics-tls
  rules:
  - host: robotics.your-institution.edu
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: robotics-api-service
            port:
              number: 80
```

#### Azure Deployment

**ARM Template:**
```json
{
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "location": {
            "type": "string",
            "defaultValue": "[resourceGroup().location]"
        },
        "vmName": {
            "type": "string",
            "defaultValue": "robotics-vm"
        },
        "adminUsername": {
            "type": "string"
        },
        "adminPassword": {
            "type": "securestring"
        },
        "vmSize": {
            "type": "string",
            "defaultValue": "Standard_D8s_v3"
        }
    },
    "variables": {
        "storageAccountName": "[concat('robotics', uniqueString(resourceGroup().id))]",
        "networkSecurityGroupName": "[concat(parameters('vmName'), '-nsg')]",
        "virtualNetworkName": "[concat(parameters('vmName'), '-vnet')]",
        "publicIpAddressName": "[concat(parameters('vmName'), '-pip')]",
        "subnetName": "default",
        "nicName": "[concat(parameters('vmName'), '-nic')]"
    },
    "resources": [
        {
            "type": "Microsoft.Network/networkSecurityGroups",
            "apiVersion": "2022-07-01",
            "name": "[variables('networkSecurityGroupName')]",
            "location": "[parameters('location')]",
            "properties": {
                "securityRules": [
                    {
                        "name": "SSH",
                        "properties": {
                            "priority": 1000,
                            "protocol": "TCP",
                            "access": "Allow",
                            "direction": "Inbound",
                            "sourceAddressPrefix": "*",
                            "sourcePortRange": "*",
                            "destinationAddressPrefix": "*",
                            "destinationPortRange": "22"
                        }
                    },
                    {
                        "name": "HTTP",
                        "properties": {
                            "priority": 1001,
                            "protocol": "TCP",
                            "access": "Allow",
                            "direction": "Inbound",
                            "sourceAddressPrefix": "*",
                            "sourcePortRange": "*",
                            "destinationAddressPrefix": "*",
                            "destinationPortRange": "80"
                        }
                    },
                    {
                        "name": "HTTPS",
                        "properties": {
                            "priority": 1002,
                            "protocol": "TCP",
                            "access": "Allow",
                            "direction": "Inbound",
                            "sourceAddressPrefix": "*",
                            "sourcePortRange": "*",
                            "destinationAddressPrefix": "*",
                            "destinationPortRange": "443"
                        }
                    }
                ]
            }
        },
        {
            "type": "Microsoft.Network/virtualNetworks",
            "apiVersion": "2022-07-01",
            "name": "[variables('virtualNetworkName')]",
            "location": "[parameters('location')]",
            "dependsOn": [
                "[resourceId('Microsoft.Network/networkSecurityGroups', variables('networkSecurityGroupName'))]"
            ],
            "properties": {
                "addressSpace": {
                    "addressPrefixes": [
                        "10.0.0.0/16"
                    ]
                },
                "subnets": [
                    {
                        "name": "[variables('subnetName')]",
                        "properties": {
                            "addressPrefix": "10.0.0.0/24",
                            "networkSecurityGroup": {
                                "id": "[resourceId('Microsoft.Network/networkSecurityGroups', variables('networkSecurityGroupName'))]"
                            }
                        }
                    }
                ]
            }
        },
        {
            "type": "Microsoft.Network/publicIPAddresses",
            "apiVersion": "2022-07-01",
            "name": "[variables('publicIpAddressName')]",
            "location": "[parameters('location')]",
            "properties": {
                "publicIPAllocationMethod": "Dynamic"
            }
        },
        {
            "type": "Microsoft.Network/networkInterfaces",
            "apiVersion": "2022-07-01",
            "name": "[variables('nicName')]",
            "location": "[parameters('location')]",
            "dependsOn": [
                "[resourceId('Microsoft.Network/virtualNetworks', variables('virtualNetworkName'))]",
                "[resourceId('Microsoft.Network/publicIPAddresses', variables('publicIpAddressName'))]"
            ],
            "properties": {
                "ipConfigurations": [
                    {
                        "name": "ipconfig1",
                        "properties": {
                            "privateIPAllocationMethod": "Dynamic",
                            "publicIPAddress": {
                                "id": "[resourceId('Microsoft.Network/publicIPAddresses', variables('publicIpAddressName'))]"
                            },
                            "subnet": {
                                "id": "[resourceId('Microsoft.Network/virtualNetworks/subnets', variables('virtualNetworkName'), variables('subnetName'))]"
                            }
                        }
                    }
                ]
            }
        },
        {
            "type": "Microsoft.Compute/virtualMachines",
            "apiVersion": "2022-11-01",
            "name": "[parameters('vmName')]",
            "location": "[parameters('location')]",
            "dependsOn": [
                "[resourceId('Microsoft.Network/networkInterfaces', variables('nicName'))]"
            ],
            "properties": {
                "hardwareProfile": {
                    "vmSize": "[parameters('vmSize')]"
                },
                "osProfile": {
                    "computerName": "[parameters('vmName')]",
                    "adminUsername": "[parameters('adminUsername')]",
                    "adminPassword": "[parameters('adminPassword')]"
                },
                "storageProfile": {
                    "imageReference": {
                        "publisher": "Canonical",
                        "offer": "0001-com-ubuntu-server-focal",
                        "sku": "20_04-lts-gen2",
                        "version": "latest"
                    },
                    "osDisk": {
                        "createOption": "FromImage",
                        "managedDisk": {
                            "storageAccountType": "Premium_LRS"
                        },
                        "diskSizeGb": 128
                    }
                },
                "networkProfile": {
                    "networkInterfaces": [
                        {
                            "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('nicName'))]"
                        }
                    ]
                }
            }
        }
    ]
}
```

### 3. Hybrid Deployment

#### On-Premises + Cloud Integration

**Architecture:**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   On-Premises   │────│   VPN/Express   │────│   Cloud         │
│   (Simulation)  │    │   Route         │    │   (API, DB)     │
│   High Compute  │    │   Connection    │    │   Management    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Students       │
                    │  (Web Access)   │
                    └─────────────────┘
```

**Configuration:**
```bash
# 1. Set up VPN connection between on-premises and cloud
# Using AWS Site-to-Site VPN as example

# On on-premises firewall/router, configure:
# - Customer gateway with cloud provider
# - Virtual private gateway
# - VPN connection
# - Route tables

# 2. Configure on-premises simulation servers
# Install simulation software and ROS 2
sudo apt update
sudo apt install ros-humble-gazebo-* ros-humble-ignition-*

# Configure ROS 2 to communicate with cloud
echo "export ROS_DOMAIN_ID=42" >> ~/.bashrc
echo "export ROS_DISCOVERY_SERVER=cloud-api-server:11811" >> ~/.bashrc

# 3. Set up reverse proxy to route simulation requests
# nginx configuration
upstream simulation_servers {
    server sim1.onprem.edu:11345;
    server sim2.onprem.edu:11345;
}

server {
    listen 80;
    server_name robotics.your-institution.edu;

    location /simulation/ {
        proxy_pass http://simulation_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location / {
        proxy_pass http://cloud_frontend;
    }
}
```

## Institutional Integration

### 1. Single Sign-On (SSO) Integration

#### SAML Integration
```python
# saml_integration.py
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from flask import Flask, request, session, redirect, url_for
import json

app = Flask(__name__)

def init_saml_auth(req):
    """Initialize SAML authentication"""
    auth = OneLogin_Saml2_Auth(req, custom_base_path='saml')
    return auth

@app.route('/sso/login')
def sso_login():
    """Initiate SAML login"""
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)
    sso_built_url = auth.login()
    session['AuthNRequestID'] = auth.get_last_request_id()
    return redirect(sso_built_url)

@app.route('/sso/acs', methods=['POST'])
def sso_acs():
    """Handle SAML assertion consumer service"""
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)

    auth.process_response()
    errors = auth.get_errors()

    if not errors:
        if 'AuthNRequestID' in session:
            del session['AuthNRequestID']

        session['samlUserdata'] = auth.get_attributes()
        session['samlNameId'] = auth.get_nameid()
        session['samlSessionIndex'] = auth.get_session_index()

        # Create local user account if doesn't exist
        user_info = {
            'email': auth.get_attributes().get('email', [''])[0],
            'first_name': auth.get_attributes().get('firstName', [''])[0],
            'last_name': auth.get_attributes().get('lastName', [''])[0],
            'student_id': auth.get_attributes().get('eduPersonPrincipalName', [''])[0],
        }

        # Sync with local user database
        sync_user_with_local_db(user_info)

        return redirect(url_for('dashboard'))
    else:
        return f"SAML Error: {errors}"

def prepare_flask_request(request):
    """Prepare Flask request for SAML"""
    url_data = request.url.split('/')
    return {
        'https': 'on' if request.scheme == 'https' else 'off',
        'http_host': request.host,
        'server_port': request.environ.get('SERVER_PORT'),
        'script_name': request.path,
        'get_data': request.args.copy(),
        'post_data': request.form.copy(),
        'query_string': request.query_string
    }

def sync_user_with_local_db(user_info):
    """Sync SAML user info with local database"""
    # Implementation to create/update user in local database
    pass
```

#### OAuth 2.0 Integration
```python
# oauth_integration.py
from authlib.integrations.flask_client import OAuth
from flask import Flask, session, redirect, url_for, request
import requests

app = Flask(__name__)
oauth = OAuth(app)

# Configure OAuth for institutional identity provider
institution_oauth = oauth.register(
    name='institution',
    client_id='your-client-id',
    client_secret='your-client-secret',
    server_metadata_url='https://auth.your-institution.edu/.well-known/openid_configuration',
    client_kwargs={
        'scope': 'openid profile email'
    }
)

@app.route('/login')
def login():
    """Initiate OAuth login"""
    redirect_uri = url_for('auth_callback', _external=True)
    return institution_oauth.authorize_redirect(redirect_uri)

@app.route('/auth/callback')
def auth_callback():
    """Handle OAuth callback"""
    token = institution_oauth.authorize_access_token()
    user_info = institution_oauth.parse_id_token(token)

    # Extract user information
    email = user_info.get('email')
    name = user_info.get('name')
    sub = user_info.get('sub')  # Unique identifier

    # Create or update local user
    local_user = get_or_create_local_user(email, name, sub)

    # Set session
    session['user_id'] = local_user.id
    session['user_email'] = email

    return redirect(url_for('dashboard'))

def get_or_create_local_user(email, name, external_id):
    """Get or create local user from institutional auth"""
    # Implementation to find or create user in local database
    pass
```

### 2. Learning Management System (LMS) Integration

#### LTI 1.3 Integration
```python
# lti_integration.py
from pylti1p3.contrib.flask import FlaskMessageLaunch, FlaskRequest, FlaskCacheDataStorage
from pylti1p3.tool_config import ToolConfDict
from pylti1p3.request import Request
import json

class LTIConfig:
    def __init__(self):
        self.config = {
            "https://lms.your-institution.edu": {
                "client_id": "your-lti-client-id",
                "auth_login_url": "https://lms.your-institution.edu/api/lti/authorize_redirect",
                "auth_token_url": "https://lms.your-institution.edu/api/lti/token",
                "key_set_url": "https://lms.your-institution.edu/api/lti/certs",
                "private_key_file": "path/to/private/key.pem",
                "deployment_ids": ["your-deployment-id"]
            }
        }

@app.route('/lti/launch', methods=['POST'])
def lti_launch():
    """Handle LTI 1.3 launch"""
    request = FlaskRequest()
    config = LTIConfig()
    conf = ToolConfDict(config.config)

    launch = FlaskMessageLaunch(request, conf, cache=FlaskCacheDataStorage())

    if launch.is_valid():
        # Get user information
        user_info = launch.get_launch_data()
        user_email = user_info.get('email')
        user_name = user_info.get('name')

        # Get course information
        course_info = launch.get_course_info()
        course_id = course_info.get('id')

        # Create or update user in system
        local_user = sync_lti_user(user_email, user_name, course_id)

        # Set session
        session['user_id'] = local_user.id
        session['course_id'] = course_id

        # Redirect to appropriate course content
        return redirect(url_for('course_content', course_id=course_id))
    else:
        return "Invalid LTI launch", 400

def sync_lti_user(email, name, course_id):
    """Sync LTI user with local system"""
    # Implementation to create/update user based on LTI data
    pass
```

### 3. Database Integration

#### LDAP/Active Directory Integration
```python
# ldap_integration.py
import ldap3
from ldap3 import Server, Connection, ALL, SUBTREE
from typing import Dict, Optional

class LDAPIntegration:
    def __init__(self, server_url: str, bind_dn: str, bind_password: str, base_dn: str):
        self.server = Server(server_url, get_info=ALL)
        self.bind_dn = bind_dn
        self.bind_password = bind_password
        self.base_dn = base_dn

    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate user against LDAP"""
        try:
            with Connection(self.server, user=f"cn={username},{self.base_dn}", password=password) as conn:
                return conn.bind()
        except Exception as e:
            print(f"LDAP authentication error: {e}")
            return False

    def get_user_info(self, username: str) -> Optional[Dict]:
        """Get user information from LDAP"""
        try:
            with Connection(self.server, user=self.bind_dn, password=self.bind_password) as conn:
                conn.bind()

                search_filter = f"(cn={username})"
                conn.search(
                    search_base=self.base_dn,
                    search_filter=search_filter,
                    search_scope=SUBTREE,
                    attributes=['cn', 'mail', 'givenName', 'sn', 'memberOf']
                )

                if conn.entries:
                    entry = conn.entries[0]
                    return {
                        'username': entry.cn.value if entry.cn else username,
                        'email': entry.mail.value if entry.mail else None,
                        'first_name': entry.givenName.value if entry.givenName else None,
                        'last_name': entry.sn.value if entry.sn else None,
                        'groups': entry.memberOf.values if entry.memberOf else []
                    }
        except Exception as e:
            print(f"LDAP search error: {e}")

        return None

    def sync_users(self) -> int:
        """Sync all users from LDAP to local database"""
        try:
            with Connection(self.server, user=self.bind_dn, password=self.bind_password) as conn:
                conn.bind()

                # Search for all students
                conn.search(
                    search_base=self.base_dn,
                    search_filter="(departmentNumber=Robotics)",
                    search_scope=SUBTREE,
                    attributes=['cn', 'mail', 'givenName', 'sn']
                )

                synced_count = 0
                for entry in conn.entries:
                    user_data = {
                        'username': entry.cn.value,
                        'email': entry.mail.value,
                        'first_name': entry.givenName.value,
                        'last_name': entry.sn.value
                    }
                    # Sync to local database
                    sync_user_to_local_db(user_data)
                    synced_count += 1

                return synced_count
        except Exception as e:
            print(f"LDAP sync error: {e}")
            return 0

def sync_user_to_local_db(user_data: Dict):
    """Sync user data to local database"""
    # Implementation to sync user to local database
    pass
```

## Security and Compliance

### 1. Network Security

#### Firewall Configuration
```bash
# ufw configuration for robotics course server
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow ROS 2 communication
sudo ufw allow 11311:11411/udp
sudo ufw allow 11311:11411/tcp

# Allow Gazebo simulation
sudo ufw allow 11345/udp

# Allow database access (internal only)
sudo ufw allow from 10.0.0.0/8 to any port 5432 proto tcp

# Enable firewall
sudo ufw enable
```

#### SSL/TLS Configuration
```nginx
# nginx SSL configuration
server {
    listen 443 ssl http2;
    server_name robotics.your-institution.edu;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    location / {
        proxy_pass http://backend_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. Backup and Disaster Recovery

#### Automated Backup Script
```bash
#!/bin/bash
# backup_script.sh

# Configuration
BACKUP_DIR="/backup/robotics-course"
DATABASE_NAME="robotics_course"
DB_USER="backup_user"
DB_PASSWORD="secure_password"
RETENTION_DAYS=30

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Get current date for backup filename
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
echo "Starting database backup..."
pg_dump -U "$DB_USER" -h localhost -d "$DATABASE_NAME" > "$BACKUP_DIR/db_backup_$DATE.sql"

# Backup application data
echo "Starting application data backup..."
tar -czf "$BACKUP_DIR/app_data_$DATE.tar.gz" -C /app/data .

# Backup configuration files
echo "Starting configuration backup..."
tar -czf "$BACKUP_DIR/config_backup_$DATE.tar.gz" -C /etc/robotics-course .

# Compress and encrypt backup (optional)
if command -v gpg &> /dev/null; then
    gpg --symmetric --cipher-algo AES256 --output "$BACKUP_DIR/encrypted_backup_$DATE.gpg" "$BACKUP_DIR/db_backup_$DATE.sql"
    rm "$BACKUP_DIR/db_backup_$DATE.sql"  # Remove unencrypted backup
fi

# Upload to cloud storage (optional)
if command -v aws &> /dev/null; then
    aws s3 cp "$BACKUP_DIR/" s3://your-backup-bucket/robotics-course/ --recursive --exclude "*" --include "*_$DATE.*"
fi

# Remove old backups
find "$BACKUP_DIR" -name "*.sql" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.gpg" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $(date)"
```

#### Backup Schedule (Cron)
```bash
# Add to crontab: crontab -e
# Daily backup at 2 AM
0 2 * * * /path/to/backup_script.sh

# Weekly full backup on Sundays at 1 AM
0 1 * * 0 /path/to/full_backup_script.sh

# Monthly cleanup on first day of month at 3 AM
0 3 1 * * /path/to/cleanup_old_backups.sh
```

## Monitoring and Maintenance

### 1. System Monitoring

#### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'robotics-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: /metrics
    scrape_interval: 10s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['localhost:9187']

  - job_name: 'ros-monitoring'
    static_configs:
      - targets: ['localhost:9090']
```

#### Grafana Dashboard Configuration
```json
{
  "dashboard": {
    "id": null,
    "title": "Robotics Course Monitoring",
    "tags": ["robotics", "course"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "API Requests",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ],
        "xaxis": {
          "mode": "time"
        }
      },
      {
        "id": 2,
        "title": "System Resources",
        "type": "row",
        "panels": [
          {
            "id": 3,
            "title": "CPU Usage",
            "type": "singlestat",
            "targets": [
              {
                "expr": "100 - (avg by(instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
                "refId": "A"
              }
            ],
            "format": "percent",
            "prefix": "",
            "postfix": "%"
          },
          {
            "id": 4,
            "title": "Memory Usage",
            "type": "singlestat",
            "targets": [
              {
                "expr": "(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100",
                "refId": "A"
              }
            ],
            "format": "percent",
            "prefix": "",
            "postfix": "%"
          }
        ]
      }
    ],
    "time": {
      "from": "now-6h",
      "to": "now"
    }
  }
}
```

### 2. Health Checks and Maintenance

#### Health Check Endpoint
```python
# health_check.py
from flask import Flask, jsonify
import subprocess
import socket
import time

app = Flask(__name__)

@app.route('/health')
def health_check():
    """Comprehensive health check"""
    checks = {
        'database': check_database(),
        'redis': check_redis(),
        'ros_connection': check_ros_connection(),
        'disk_space': check_disk_space(),
        'memory_usage': check_memory_usage(),
        'api_responsiveness': check_api_responsiveness()
    }

    overall_status = all(check['status'] for check in checks.values())

    return jsonify({
        'status': 'healthy' if overall_status else 'unhealthy',
        'timestamp': time.time(),
        'checks': checks
    })

def check_database():
    """Check database connectivity"""
    try:
        # Implementation to check database connection
        # This is a placeholder
        return {'status': True, 'message': 'Database connected'}
    except Exception as e:
        return {'status': False, 'message': str(e)}

def check_redis():
    """Check Redis connectivity"""
    try:
        # Implementation to check Redis connection
        return {'status': True, 'message': 'Redis connected'}
    except Exception as e:
        return {'status': False, 'message': str(e)}

def check_ros_connection():
    """Check ROS master connectivity"""
    try:
        # Check if ROS master is running
        result = subprocess.run(['ros2', 'node', 'list'], capture_output=True, text=True, timeout=5)
        return {'status': result.returncode == 0, 'message': 'ROS connected' if result.returncode == 0 else 'ROS not responding'}
    except Exception as e:
        return {'status': False, 'message': str(e)}

def check_disk_space():
    """Check available disk space"""
    try:
        result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
        output = result.stdout.split('\n')[1].split()
        usage_percent = int(output[4].rstrip('%'))

        if usage_percent > 80:
            return {'status': False, 'message': f'Disk usage high: {usage_percent}%'}
        else:
            return {'status': True, 'message': f'Disk usage: {usage_percent}%'}
    except Exception as e:
        return {'status': False, 'message': str(e)}

def check_memory_usage():
    """Check memory usage"""
    try:
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()

        mem_total = int(lines[0].split()[1])
        mem_available = int(lines[1].split()[1])
        mem_usage = (mem_total - mem_available) / mem_total * 100

        if mem_usage > 80:
            return {'status': False, 'message': f'Memory usage high: {mem_usage:.1f}%'}
        else:
            return {'status': True, 'message': f'Memory usage: {mem_usage:.1f}%'}
    except Exception as e:
        return {'status': False, 'message': str(e)}

def check_api_responsiveness():
    """Check API responsiveness"""
    try:
        start_time = time.time()
        # Make a simple API call
        # Implementation would make actual API call
        response_time = (time.time() - start_time) * 1000

        if response_time > 1000:  # More than 1 second
            return {'status': False, 'message': f'API slow: {response_time:.0f}ms'}
        else:
            return {'status': True, 'message': f'API responsive: {response_time:.0f}ms'}
    except Exception as e:
        return {'status': False, 'message': str(e)}
```

## Performance Optimization

### 1. Caching Strategy

#### Redis Configuration
```bash
# redis.conf
# Basic configuration for course platform
bind 127.0.0.1
port 6379
timeout 300
tcp-keepalive 300

# Memory management
maxmemory 2gb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000

# Log level
loglevel notice
logfile /var/log/redis/redis-server.log

# Security
requirepass your_secure_password
rename-command FLUSHDB ""
rename-command FLUSHALL ""
```

### 2. Load Balancing

#### Nginx Load Balancer Configuration
```nginx
# nginx.conf
upstream backend_servers {
    least_conn;
    server api1.robotics.edu:8000 max_fails=3 fail_timeout=30s;
    server api2.robotics.edu:8000 max_fails=3 fail_timeout=30s;
    server api3.robotics.edu:8000 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name robotics.your-institution.edu;

    location / {
        proxy_pass http://backend_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Connection pooling
        proxy_http_version 1.1;
        proxy_set_header Connection "";

        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://backend_servers/health;
    }
}
```

This comprehensive deployment guide provides:

1. **Multiple Architecture Options**: From single server to cloud-based deployments
2. **Institutional Integration**: SSO, LMS, and directory service integration
3. **Security Measures**: Network security, SSL/TLS, and compliance considerations
4. **Backup and Recovery**: Automated backup solutions and disaster recovery plans
5. **Monitoring and Maintenance**: Health checks, monitoring tools, and maintenance procedures
6. **Performance Optimization**: Caching, load balancing, and optimization strategies

The guide covers various institutional needs from small departments to large universities, ensuring the Physical AI & Humanoid Robotics course can be deployed successfully in diverse environments while maintaining security, performance, and reliability.

Last updated: December 13, 2025