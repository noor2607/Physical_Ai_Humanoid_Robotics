---
title: "Cloud and Backup Solutions"
sidebar_label: "Cloud & Backup Solutions"
sidebar_position: 108
---

# Cloud and Backup Solutions for Different Hardware Setups

## Overview

This guide provides comprehensive information about cloud-based alternatives and backup solutions for the Physical AI & Humanoid Robotics course. When local hardware is insufficient or unavailable, cloud platforms provide accessible alternatives for completing course exercises and projects.

## Cloud Platform Options

### 1. Amazon Web Services (AWS)

#### EC2 GPU Instances
- **Recommended Instance Types**:
  - `g4dn.xlarge`: 1 GPU, 4 vCPUs, 16 GB RAM, 125 GB storage
  - `g4dn.2xlarge`: 1 GPU, 8 vCPUs, 32 GB RAM, 225 GB storage
  - `p3.2xlarge`: 1 V100 GPU, 8 vCPUs, 61 GB RAM, EBS storage

#### Setup Guide
```bash
# 1. Launch EC2 instance with appropriate AMI
# Ubuntu 22.04 LTS with NVIDIA drivers pre-installed

# 2. Install ROS 2 Humble Hawksbill
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update
sudo apt install curl gnupg lsb-release
curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | sudo gpg --dearmor -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
sudo apt update
sudo apt install ros-humble-desktop
sudo apt install python3-rosdep python3-rosinstall python3-rosinstall-generator python3-vcstool build-essential

# 3. Install simulation environments
sudo apt install gazebo11 gz-tools1
pip3 install --user setuptools==58.2.0  # For Isaac Sim compatibility

# 4. Initialize rosdep
sudo rosdep init
rosdep update

# 5. Source ROS 2 environment
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

#### Cost Optimization Tips
- Use **Spot Instances** for up to 70% cost savings (interruptible)
- Use **Reserved Instances** for predictable long-term usage
- Terminate instances when not in use
- Use smaller instances for development, larger for simulation

### 2. Microsoft Azure

#### Azure VMs with GPU
- **Recommended Series**:
  - `NC6s_v3`: 1 NVIDIA Tesla V100, 6 vCPUs, 112 GB RAM
  - `NC12s_v3`: 2 NVIDIA Tesla V100, 12 vCPUs, 224 GB RAM
  - `ND40rs_v2`: 8 NVIDIA Tesla V100, 40 vCPUs, 672 GB RAM

#### Setup Guide
```bash
# 1. Create Azure VM with GPU
# Use Azure CLI or Azure Portal

# 2. Install NVIDIA drivers
wget https://us.download.nvidia.com/tesla/535.54.03/NVIDIA-Linux-x86_64-535.54.03.run
sudo sh NVIDIA-Linux-x86_64-535.54.03.run

# 3. Install Docker and nvidia-docker
sudo apt update
sudo apt install docker.io
sudo usermod -aG docker $USER

# Install nvidia-docker2
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt update
sudo apt install nvidia-docker2
sudo systemctl restart docker
```

### 3. Google Cloud Platform (GCP)

#### Compute Engine with GPUs
- **Recommended Configurations**:
  - `n1-standard-4` with 1x K80: 4 vCPUs, 15 GB RAM, 1 GPU
  - `n1-standard-8` with 1x P4: 8 vCPUs, 30 GB RAM, 1 GPU
  - `a2-highgpu-1g`: 12 vCPUs, 85 GB RAM, 1x A100

#### Setup Guide
```bash
# 1. Create VM instance with GPU
# Use gcloud CLI or Cloud Console

# 2. Install CUDA and drivers
sudo apt update
sudo apt install -y build-essential dkms
wget https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda_12.1.0_530.30.02_linux.run
sudo sh cuda_12.1.0_530.30.02_linux.run

# 3. Install ROS 2
# Follow same steps as AWS setup
```

### 4. Cloud-Based Development Environments

#### GitHub Codespaces
- **Configuration** for Physical AI course:
```json
{
  "name": "Physical AI & Robotics Development",
  "image": "mcr.microsoft.com/vscode/devcontainers/universal:2-linux",
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {},
    "ghcr.io/devcontainers/features/python:1": {
      "version": "3.10"
    }
  },
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-iot.vscode-ros",
        "ms-iot.vscode-ros-docs"
      ]
    }
  },
  "postCreateCommand": "bash .devcontainer/post-create.sh"
}
```

#### GitPod
- **Configuration** (.gitpod.yml):
```yaml
image: gitpod/workspace-full:2023-11-21-09-03-40

tasks:
  - name: ROS 2 Setup
    init: |
      sudo apt update
      sudo apt install -y curl gnupg lsb-release
      curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | sudo gpg --dearmor -o /usr/share/keyrings/ros-archive-keyring.gpg
      echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
      sudo apt update
      sudo apt install -y ros-humble-desktop
      echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
      source ~/.bashrc
    command: |
      echo "ROS 2 Humble setup complete!"

vscode:
  extensions:
    - ms-python.python
    - ms-iot.vscode-ros
```

## Container-Based Solutions

### Docker for Cloud Deployment

#### Base Dockerfile for Course
```dockerfile
# Dockerfile.course
FROM osrf/ros:humble-desktop-full

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-colcon-common-extensions \
    python3-rosdep \
    wget \
    curl \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 install --upgrade pip && \
    pip3 install \
    numpy \
    scipy \
    matplotlib \
    pandas \
    jupyter \
    speechrecognition \
    openai \
    transformers

# Set up ROS workspace
RUN mkdir -p /workspace/src
WORKDIR /workspace

# Source ROS environment
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
RUN echo "source /workspace/install/setup.bash" >> ~/.bashrc

# Create entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
```

#### Docker Compose for Multi-Container Setup
```yaml
# docker-compose.yml
version: '3.8'

services:
  ros-core:
    build: .
    container_name: ros_humble_core
    environment:
      - ROS_DOMAIN_ID=42
      - DISPLAY=${DISPLAY}
    volumes:
      - /tmp/.X11-unix:/tmp/.X11-unix:rw
      - ./src:/workspace/src
      - ./exercises:/workspace/exercises
    network_mode: host
    stdin_open: true
    tty: true

  gazebo:
    build: .
    container_name: gazebo_sim
    environment:
      - DISPLAY=${DISPLAY}
      - GAZEBO_MODEL_DATABASE_URI=""
    volumes:
      - /tmp/.X11-unix:/tmp/.X11-unix:rw
      - ./models:/root/.gazebo/models
    ports:
      - "11345:11345/udp"
    depends_on:
      - ros-core

  isaac-sim:
    image: nvidia/isaac-sim:4.0.0
    container_name: isaac_sim
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=all
      - DISPLAY=${DISPLAY}
    volumes:
      - /tmp/.X11-unix:/tmp/.X11-unix:rw
      - ./isaac_assets:/isaac_assets
    ports:
      - "55555:55555"
    depends_on:
      - ros-core
```

### Kubernetes for Scalable Deployments

#### Kubernetes Manifest for Course Environment
```yaml
# k8s-course-environment.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: robotics-course

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: course-storage
  namespace: robotics-course
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ros-environment
  namespace: robotics-course
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ros-environment
  template:
    metadata:
      labels:
        app: ros-environment
    spec:
      containers:
      - name: ros-core
        image: your-registry/ros-humble-course:latest
        ports:
        - containerPort: 11311
        env:
        - name: ROS_DOMAIN_ID
          value: "42"
        volumeMounts:
        - name: course-storage
          mountPath: /workspace
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
      volumes:
      - name: course-storage
        persistentVolumeClaim:
          claimName: course-storage

---
apiVersion: v1
kind: Service
metadata:
  name: ros-service
  namespace: robotics-course
spec:
  selector:
    app: ros-environment
  ports:
  - port: 11311
    targetPort: 11311
  type: ClusterIP
```

## Backup and Recovery Strategies

### 1. Local Development Backup

#### Git-Based Backup
```bash
# Set up Git repository for course work
mkdir ~/robotics-course-work
cd ~/robotics-course-work
git init

# Add all course files
git add .
git commit -m "Initial course work backup"
git remote add origin https://github.com/your-username/robotics-course-backup.git
git push -u origin main

# Regular backup workflow
git add .
git commit -m "Backup - $(date)"
git push
```

#### Automated Backup Script
```bash
#!/bin/bash
# backup_course_work.sh

COURSE_DIR="$HOME/robotics-course-work"
BACKUP_DIR="$HOME/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create compressed backup
tar -czf "$BACKUP_DIR/course_backup_$DATE.tar.gz" -C "$(dirname $COURSE_DIR)" "$(basename $COURSE_DIR)"

# Keep only last 7 backups
find "$BACKUP_DIR" -name "course_backup_*.tar.gz" -mtime +7 -delete

# Optional: Upload to cloud storage
if command -v aws &> /dev/null; then
    aws s3 cp "$BACKUP_DIR/course_backup_$DATE.tar.gz" s3://your-backup-bucket/
fi

echo "Backup completed: course_backup_$DATE.tar.gz"
```

### 2. Cloud Storage Integration

#### AWS S3 Backup
```python
# s3_backup.py
import boto3
import os
from datetime import datetime
import tarfile
import tempfile

def backup_to_s3(local_dir, bucket_name, s3_prefix="backups"):
    """Backup local directory to S3"""
    s3_client = boto3.client('s3')

    # Create timestamped archive
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"course_backup_{timestamp}.tar.gz"

    # Create temporary archive
    with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as temp_file:
        with tarfile.open(temp_file.name, "w:gz") as tar:
            tar.add(local_dir, arcname=os.path.basename(local_dir))

        # Upload to S3
        s3_key = f"{s3_prefix}/{archive_name}"
        s3_client.upload_file(temp_file.name, bucket_name, s3_key)

        # Clean up temporary file
        os.unlink(temp_file.name)

    print(f"Backup uploaded to s3://{bucket_name}/{s3_key}")

# Usage
backup_to_s3("~/robotics-course-work", "my-course-backups")
```

#### Google Drive Backup
```python
# drive_backup.py
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os
import zipfile
from datetime import datetime

def backup_to_drive(local_dir, folder_name="Course Backups"):
    """Backup local directory to Google Drive"""
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()  # Creates local webserver and auto handles authentication

    drive = GoogleDrive(gauth)

    # Find or create backup folder
    folder_list = drive.ListFile({'q': f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder'"}).GetList()

    if folder_list:
        folder_id = folder_list[0]['id']
    else:
        # Create new folder
        folder_metadata = {
            'title': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = drive.CreateFile(folder_metadata)
        folder.Upload()
        folder_id = folder['id']

    # Create timestamped zip file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"course_backup_{timestamp}.zip"

    # Create zip archive
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(local_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(local_dir))
                zipf.write(file_path, arcname)

    # Upload to Drive
    file_metadata = {
        'title': zip_name,
        'parents': [{'id': folder_id}]
    }
    file_drive = drive.CreateFile(file_metadata)
    file_drive.SetContentFile(zip_name)
    file_drive.Upload()

    # Clean up local zip file
    os.remove(zip_name)

    print(f"Backup uploaded to Google Drive: {zip_name}")

# Usage
backup_to_drive("~/robotics-course-work")
```

## Hybrid Local-Cloud Workflow

### Development Workflow with Cloud Fallback

#### Sync Script for Local-Cloud Sync
```bash
#!/bin/bash
# sync_local_cloud.sh

LOCAL_WORK_DIR="$HOME/robotics-course-work"
REMOTE_HOST="your-cloud-instance"
REMOTE_DIR="/home/ubuntu/robotics-course-work"

# Sync from local to cloud (push changes)
sync_to_cloud() {
    echo "Syncing local changes to cloud..."
    rsync -avz --exclude '__pycache__' --exclude '.git' "$LOCAL_WORK_DIR/" "$REMOTE_HOST:$REMOTE_DIR/"
    echo "Sync to cloud completed."
}

# Sync from cloud to local (pull changes)
sync_from_cloud() {
    echo "Syncing cloud changes to local..."
    rsync -avz --exclude '__pycache__' --exclude '.git' "$REMOTE_HOST:$REMOTE_DIR/" "$LOCAL_WORK_DIR/"
    echo "Sync from cloud completed."
}

# Choose operation
case $1 in
    "push")
        sync_to_cloud
        ;;
    "pull")
        sync_from_cloud
        ;;
    "both")
        sync_to_cloud
        sync_from_cloud
        ;;
    *)
        echo "Usage: $0 {push|pull|both}"
        exit 1
        ;;
esac
```

### Cloud-Based Development with Local Testing

#### Remote Development Setup
```python
# remote_dev_config.py
import os
from pathlib import Path

class RemoteDevelopmentConfig:
    def __init__(self):
        self.is_remote = self._detect_remote_environment()
        self.storage_path = self._get_storage_path()
        self.compute_resources = self._detect_compute_resources()

    def _detect_remote_environment(self):
        """Detect if running in cloud environment"""
        # Check for cloud-specific environment variables
        cloud_env_vars = [
            'AWS_EXECUTION_ENV',
            'GOOGLE_CLOUD_PROJECT',
            'AZURE_SUBSCRIPTION_ID',
            'KUBERNETES_SERVICE_HOST'
        ]

        for var in cloud_env_vars:
            if os.environ.get(var):
                return True

        # Check for cloud-specific files
        cloud_files = [
            '/sys/class/dmi/id/product_name',
            '/sys/class/dmi/id/chassis_asset_tag'
        ]

        for file_path in cloud_files:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read().strip().lower()
                    if any(cloud_provider in content for cloud_provider in ['amazon', 'google', 'microsoft', 'azure']):
                        return True

        return False

    def _get_storage_path(self):
        """Get appropriate storage path based on environment"""
        if self.is_remote:
            # Use cloud storage
            return "/workspace/storage"
        else:
            # Use local storage
            return str(Path.home() / "robotics-course-work")

    def _detect_compute_resources(self):
        """Detect available compute resources"""
        import psutil
        import GPUtil

        resources = {
            'cpu_count': psutil.cpu_count(),
            'memory_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'gpus': []
        }

        # Detect GPUs
        gpus = GPUtil.getGPUs()
        for gpu in gpus:
            resources['gpus'].append({
                'id': gpu.id,
                'name': gpu.name,
                'memory_total': gpu.memoryTotal,
                'memory_free': gpu.memoryFree
            })

        return resources

# Usage
config = RemoteDevelopmentConfig()
print(f"Remote environment: {config.is_remote}")
print(f"Storage path: {config.storage_path}")
print(f"Resources: {config.compute_resources}")
```

## Cost Management Strategies

### 1. Budget-Friendly Options

#### Free Tier Options
- **AWS Free Tier**: 750 hours/month of EC2 compute for 12 months
- **Google Cloud Free Tier**: $300 credit for first year, always-free usage
- **Azure Free Tier**: $200 credit for first month, always-free services

#### Student Discounts
- **AWS Educate**: Credits and resources for students
- **GitHub Student Developer Pack**: Free access to many development tools
- **JetBrains Students**: Free IDE licenses

### 2. Resource Optimization

#### Auto-Shutdown Scripts
```bash
#!/bin/bash
# auto_shutdown.sh

# Set idle timeout (in seconds)
IDLE_TIMEOUT=3600  # 1 hour

# Check for user activity
check_activity() {
    # Check for recent SSH connections
    if ! who | grep -q pts; then
        # Check for running ROS processes
        if ! pgrep -f "ros" > /dev/null; then
            # System is idle, schedule shutdown
            echo "System idle, scheduling shutdown in 10 minutes..."
            sudo shutdown -h +10 "Auto-shutdown due to inactivity"
        fi
    fi
}

# Run check every 10 minutes
while true; do
    check_activity
    sleep 600  # 10 minutes
done
```

#### Spot Instance Management
```python
# spot_instance_manager.py
import boto3
import time
from datetime import datetime

class SpotInstanceManager:
    def __init__(self, region='us-east-1'):
        self.ec2 = boto3.client('ec2', region_name=region)
        self.ssm = boto3.client('ssm', region_name=region)

    def create_spot_request(self, instance_type='g4dn.xlarge', max_price='0.50'):
        """Create a spot instance request"""
        response = self.ec2.request_spot_instances(
            SpotPrice=max_price,
            InstanceCount=1,
            LaunchSpecification={
                'ImageId': 'ami-0abcdef1234567890',  # Ubuntu 22.04 LTS
                'InstanceType': instance_type,
                'KeyName': 'your-key-pair',
                'SecurityGroups': ['your-security-group'],
                'UserData': '''#!/bin/bash
                # Install ROS 2 and other dependencies
                apt update
                apt install -y curl gnupg lsb-release
                curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | gpg --dearmor -o /usr/share/keyrings/ros-archive-keyring.gpg
                echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/ros2.list > /dev/null
                apt update
                apt install -y ros-humble-desktop
                echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
                '''
            }
        )

        spot_request_id = response['SpotInstanceRequests'][0]['SpotInstanceRequestId']
        print(f"Spot request created: {spot_request_id}")

        # Wait for instance to be active
        self.wait_for_instance(spot_request_id)

        return spot_request_id

    def wait_for_instance(self, spot_request_id):
        """Wait for spot instance to be active"""
        while True:
            response = self.ec2.describe_spot_instance_requests(
                SpotInstanceRequestIds=[spot_request_id]
            )

            state = response['SpotInstanceRequests'][0]['State']
            if state == 'active':
                instance_id = response['SpotInstanceRequests'][0]['InstanceId']
                print(f"Instance {instance_id} is active")
                break
            elif state == 'cancelled':
                print("Spot request was cancelled")
                break
            elif state == 'failed':
                print("Spot request failed")
                break

            time.sleep(10)

# Usage
manager = SpotInstanceManager()
spot_id = manager.create_spot_request()
```

## Security Considerations for Cloud Usage

### 1. Secure Access

#### SSH Key Management
```bash
# Generate SSH key pair for cloud access
ssh-keygen -t rsa -b 4096 -C "robotics-course@$(hostname)"

# Add to ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/robotics-course

# Configure SSH config
cat >> ~/.ssh/config << EOF
Host aws-robotics
    HostName your-instance-ip.compute-1.amazonaws.com
    User ubuntu
    IdentityFile ~/.ssh/robotics-course
    IdentitiesOnly yes

Host gcp-robotics
    HostName your-instance-external-ip
    User your-username
    IdentityFile ~/.ssh/robotics-course
    IdentitiesOnly yes
EOF
```

### 2. Network Security

#### Security Group Configuration
```bash
# AWS Security Group for Robotics Course
aws ec2 create-security-group \
    --group-name robotics-course-sg \
    --description "Security group for robotics course" \
    --vpc-id your-vpc-id

# Allow SSH from your IP only
aws ec2 authorize-security-group-ingress \
    --group-id your-sg-id \
    --protocol tcp \
    --port 22 \
    --cidr your-ip-address/32

# Allow ROS 2 communication
aws ec2 authorize-security-group-ingress \
    --group-id your-sg-id \
    --protocol tcp \
    --port 11311 \
    --source-group your-sg-id

aws ec2 authorize-security-group-ingress \
    --group-id your-sg-id \
    --protocol udp \
    --port 11311 \
    --source-group your-sg-id
```

## Migration Between Environments

### 1. Environment Configuration Transfer

#### Configuration Export Script
```python
# export_config.py
import os
import json
import subprocess
from pathlib import Path

def export_environment_config():
    """Export current environment configuration"""
    config = {
        'ros_distro': os.environ.get('ROS_DISTRO', ''),
        'ros_domain_id': os.environ.get('ROS_DOMAIN_ID', '0'),
        'python_packages': get_python_packages(),
        'system_info': get_system_info(),
        'workspace_structure': get_workspace_structure(),
        'environment_variables': get_env_vars()
    }

    with open('environment_config.json', 'w') as f:
        json.dump(config, f, indent=2)

    print("Environment configuration exported to environment_config.json")

def get_python_packages():
    """Get list of installed Python packages"""
    result = subprocess.run(['pip', 'list', '--format=json'],
                          capture_output=True, text=True)
    if result.returncode == 0:
        return json.loads(result.stdout)
    return []

def get_system_info():
    """Get system information"""
    import platform
    import psutil

    return {
        'platform': platform.platform(),
        'processor': platform.processor(),
        'cpu_count': psutil.cpu_count(),
        'memory_gb': round(psutil.virtual_memory().total / (1024**3), 2),
        'python_version': platform.python_version()
    }

def get_workspace_structure():
    """Get ROS workspace structure"""
    workspace_path = os.environ.get('ROS_WORKSPACE', os.path.expanduser('~/robotics-course-work'))
    structure = {}

    for root, dirs, files in os.walk(workspace_path):
        rel_path = os.path.relpath(root, workspace_path)
        if rel_path == '.':
            rel_path = ''
        structure[rel_path] = {
            'directories': dirs,
            'files': [f for f in files if not f.endswith('.pyc') and not f.startswith('.')]
        }

    return structure

def get_env_vars():
    """Get relevant environment variables"""
    relevant_vars = [
        'ROS_DISTRO', 'ROS_DOMAIN_ID', 'ROS_WORKSPACE',
        'PYTHONPATH', 'LD_LIBRARY_PATH', 'PATH'
    ]

    env_vars = {}
    for var in relevant_vars:
        env_vars[var] = os.environ.get(var, '')

    return env_vars

# Usage
export_environment_config()
```

### 2. Workspace Migration

#### Migration Script
```bash
#!/bin/bash
# migrate_workspace.sh

SOURCE_WORKSPACE="$1"
DESTINATION_HOST="$2"
DESTINATION_PATH="$3"

if [ -z "$SOURCE_WORKSPACE" ] || [ -z "$DESTINATION_HOST" ] || [ -z "$DESTINATION_PATH" ]; then
    echo "Usage: $0 <source_workspace> <destination_host> <destination_path>"
    exit 1
fi

echo "Migrating workspace from $SOURCE_WORKSPACE to $DESTINATION_HOST:$DESTINATION_PATH"

# Create archive of workspace (excluding build directories)
echo "Creating workspace archive..."
tar --exclude='build' --exclude='install' --exclude='log' --exclude='.git' \
    -czf workspace_backup.tar.gz -C "$(dirname $SOURCE_WORKSPACE)" "$(basename $SOURCE_WORKSPACE)"

# Transfer to destination
echo "Transferring to destination..."
scp workspace_backup.tar.gz "$DESTINATION_HOST:$DESTINATION_PATH/"

# Extract on destination
ssh "$DESTINATION_HOST" "cd $DESTINATION_PATH && tar -xzf workspace_backup.tar.gz && rm workspace_backup.tar.gz"

# Clean up local archive
rm workspace_backup.tar.gz

echo "Workspace migration completed!"
```

## Best Practices

### 1. For Students
- **Start Small**: Begin with free tier or low-cost options
- **Plan Usage**: Monitor resource usage to avoid unexpected costs
- **Regular Backups**: Maintain regular backups of important work
- **Local Development**: Use local machine for basic development, cloud for heavy simulations
- **Version Control**: Use Git to track changes and enable easy migration

### 2. For Instructors
- **Provide Templates**: Offer pre-configured cloud environments
- **Cost Monitoring**: Implement cost controls and monitoring
- **Student Support**: Provide clear documentation for cloud setup
- **Hybrid Approach**: Support both local and cloud-based workflows
- **Security**: Implement proper security measures for shared resources

### 3. For Institutions
- **Bulk Discounts**: Negotiate institutional discounts with cloud providers
- **Centralized Management**: Use centralized account management for students
- **Resource Quotas**: Implement resource quotas to control costs
- **Training**: Provide training on cloud usage and cost management
- **Monitoring**: Implement monitoring and alerting for resource usage

This comprehensive guide provides multiple options for students and institutions to access the Physical AI & Humanoid Robotics course materials, regardless of their local hardware capabilities. The solutions range from free tier options to enterprise-level deployments, ensuring accessibility for all users.

Last updated: December 13, 2025