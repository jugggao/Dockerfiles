# 构建基于 Google Cloud 命令行工具的 Kustomize 镜像

### 构建

```bash
docker build --build-arg=KUSTOMIZE_VERSION=v4.4.1 --build-arg=KUBECTL_VERSION=v1.22.0 --tag cr.oook.com.tw/tools/kustomize:v4.4.1 .
```