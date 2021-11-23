FROM alpine:3.12 AS build

ARG KUSTOMIZE_VERSION
ARG KUBECTL_VERSION

RUN apk add --no-cache wget tar
RUN wget -nv https://github.com/kubernetes-sigs/kustomize/releases/download/kustomize%2F${KUSTOMIZE_VERSION}/kustomize_${KUSTOMIZE_VERSION}_linux_amd64.tar.gz && \
    tar xvzf kustomize_${KUSTOMIZE_VERSION}_linux_amd64.tar.gz && \
    wget -nv https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl && \
    chmod 755 kubectl

FROM docker.io/google/cloud-sdk:slim

COPY --from=build kustomize /opt/google-cloud-sdk/bin/kustomize
COPY --from=build kubectl /opt/google-cloud-sdk/bin/kubectl
COPY kustomize.bash /builder/kustomize.bash
ENTRYPOINT ["/builder/kustomize.bash"]